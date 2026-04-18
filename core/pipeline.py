"""
ML pipeline — HistGBR on 30k Egyptian property dataset.
"""
from __future__ import annotations
import pickle, logging, sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd

from core.config import DATA_PATH, MODEL_PATH, MODELS_DIR, TARGET_COL, TEST_SIZE, RANDOM_STATE

logger = logging.getLogger(__name__)

COND_ORDER   = ['Needs Renovation','Fair','Good','New','Excellent']
FINISH_ORDER = ['Core & Shell','Semi Finished','Fully Finished']
FURN_ORDER   = ['Unfurnished','Partially Furnished','Furnished']
VIEW_ORDER   = ['Street','City','Garden','Pool','Sea/Lake']


@dataclass
class ModelMetrics:
    r2:float=0.0; mae:float=0.0; rmse:float=0.0
    cv_r2_mean:float=0.0; cv_r2_std:float=0.0
    n_train:int=0; n_test:int=0
    def summary(self)->dict:
        return {"R²":f"{self.r2:.4f}","MAE":f"E£{self.mae:,.0f}","RMSE":f"E£{self.rmse:,.0f}",
                "CV R²":f"{self.cv_r2_mean:.4f}±{self.cv_r2_std:.4f}",
                "Train":str(self.n_train),"Test":str(self.n_test)}


@dataclass
class PredictionInput:
    area: float; bedrooms: int; bathrooms: int; location: str
    condition: str = "Good"; finishing: str = "Fully Finished"
    furnished: str = "Unfurnished"; view: str = "Street"
    floor: int = 3; building_age: int = 5; parking: int = 1
    has_pool:int=0; has_gym:int=0; has_security:int=1
    has_elevator:int=1; has_balcony:int=1; is_compound:int=0
    garden_sqm:int=0; height_m:float=3.0
    dist_center:float=10.0; dist_metro:float=2.0

    def to_dataframe(self, payload:dict) -> pd.DataFrame:
        lm  = payload['loc_mean'];  gm  = payload['global_mean']
        lmed= payload['loc_median'];gmed= payload['global_median']
        lstd= payload['loc_std'];   gstd= payload['global_std']
        lcnt= payload['loc_count']
        tm  = payload['title_mean'];gt  = payload['global_title']
        FEATURES = payload['features']

        cond_enc   = COND_ORDER.index(self.condition)   if self.condition   in COND_ORDER   else 2
        finish_enc = FINISH_ORDER.index(self.finishing) if self.finishing   in FINISH_ORDER else 2
        furn_enc   = FURN_ORDER.index(self.furnished)   if self.furnished   in FURN_ORDER   else 0
        view_enc   = VIEW_ORDER.index(self.view)        if self.view        in VIEW_ORDER   else 0

        log_area   = float(np.log1p(self.area))
        area_sq    = float(self.area**2)
        apb        = min(self.area/max(self.bedrooms,1),400.0)
        bb         = float(self.bedrooms*self.bathrooms)
        tr         = float(self.bedrooms+self.bathrooms)
        br         = min(self.bathrooms/max(self.bedrooms,1),5.0)
        amenity    = float(self.has_pool+self.has_gym+self.has_security+
                           self.has_elevator+self.has_balcony+self.is_compound)
        age_sq     = float(self.building_age**2)
        new_bld    = 1 if self.building_age<=2 else 0
        lux        = 1 if br>1 else 0

        row = {
            'area':self.area,'log_area':log_area,'area_sq':area_sq,
            'bedrooms':self.bedrooms,'bathrooms':self.bathrooms,
            'bed_bath':bb,'total_rooms':tr,'bath_ratio':br,'area_per_bed':apb,
            'condition_enc':cond_enc,'finishing_enc':finish_enc,
            'furnished_enc':furn_enc,'view_enc':view_enc,
            'has_pool':self.has_pool,'has_gym':self.has_gym,
            'has_security':self.has_security,'has_elevator':self.has_elevator,
            'has_balcony':self.has_balcony,'is_compound':self.is_compound,
            'amenity_score':amenity,'parking_spaces':self.parking,
            'garden_sqm':self.garden_sqm,'floor_number':self.floor,
            'building_age_years':self.building_age,'age_sq':age_sq,
            'new_building':new_bld,'floor_to_ceiling_height_m':self.height_m,
            'distance_to_center_km':self.dist_center,
            'distance_to_metro_km':self.dist_metro,
            'luxury_flag':lux,
            'location_enc':lm.get(self.location,gm),
            'title_enc':gt,
        }
        return pd.DataFrame([row], columns=FEATURES)


@dataclass
class PredictionResult:
    price:float; price_low:float; price_high:float
    @property
    def formatted(self)->str: return f"E£ {self.price:,.0f}"
    @property
    def range_str(self)->str: return f"E£{self.price_low:,.0f}  –  E£{self.price_high:,.0f}"


class HousingPipeline:
    def __init__(self):
        self.model   = None; self.metrics = None
        self._payload= {}; self.locations= []; self.property_types = []
        # Expose these for backward compat (analytics.py used them directly)
        self.loc_mean={}; self.loc_median={}; self.loc_std={}; self.loc_count={}
        self.global_mean=0.0; self.global_median=0.0; self.global_std=0.0
        self.title_mean={}; self.global_title=0.0
        self._load_or_train()

    def predict(self, inp:PredictionInput)->PredictionResult:
        X=inp.to_dataframe(self._payload)
        price=float(self.model.predict(X)[0])
        price=max(price,100_000)
        return PredictionResult(price=price,price_low=price*0.88,price_high=price*1.12)

    def retrain(self)->ModelMetrics:
        MODEL_PATH.unlink(missing_ok=True)
        self._train_and_cache()
        return self.metrics

    def _load_or_train(self):
        if MODEL_PATH.exists():
            try: self._load_cached(); return
            except Exception as e: logger.warning("Cache failed (%s), retraining",e)
        self._train_and_cache()

    def _load_cached(self):
        desktop=str(Path(__file__).resolve().parent.parent)
        if desktop not in sys.path: sys.path.insert(0,desktop)
        with open(MODEL_PATH,'rb') as f: p=pickle.load(f)
        self.model=p['model']; self.metrics=p['metrics']
        self._payload=p
        # expose attributes directly for analytics.py backward compat
        self.loc_mean   =p.get('loc_mean',{})
        self.loc_median =p.get('loc_median',{})
        self.loc_std    =p.get('loc_std',{})
        self.loc_count  =p.get('loc_count',{})
        self.global_mean=float(p.get('global_mean',5e6))
        self.global_median=float(p.get('global_median',4e6))
        self.global_std=float(p.get('global_std',5e6))
        self.title_mean =p.get('title_mean',{})
        self.global_title=float(p.get('global_title',5e6))
        self.locations  =sorted(p.get('locations',[]))
        self.property_types=sorted(p.get('property_types',[]))
        logger.info("Model loaded. R²=%.4f  MAE=E£%.0f", self.metrics.r2, self.metrics.mae)

    def _train_and_cache(self):
        # Quick retrain from saved CSV
        from sklearn.ensemble import HistGradientBoostingRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error
        eng=Path(DATA_PATH.parent/'egypt_housing_engineered.csv')
        src=eng if eng.exists() else DATA_PATH
        df=pd.read_csv(src); df['location']=df['location'].fillna('Unknown')
        FEATURES=self._payload.get('features') or []
        if not FEATURES: raise RuntimeError("No feature list — please restore model pkl")
        logger.info("Retraining on %d rows…", len(df))
        # delegate to existing payload structure
