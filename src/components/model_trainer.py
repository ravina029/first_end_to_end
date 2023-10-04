import os
import sys
from dataclasses import dataclass

from catboost import CatBoostRegressor
from sklearn.ensemble import (AdaBoostRegressor, GradientBoostingRegressor, RandomForestRegressor)
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from sklearn.metrics import r2_score

from src.exception import CustomException
from src.logger import logging

from src.utils import save_object, evaluate_model 

@dataclass 
class ModelTrainerConfig:
    trained_model_file_path=os.path.join('artifacts','model.pkl')

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config=ModelTrainerConfig()

    def initiate_model_trainer(self, train_array,test_array):
        try:
            logging.info("splitting the training and test input data")
            X_train,y_train,X_test,y_test=(
                train_array[:,:-1],
                train_array[:,-1],
                test_array[:,:-1],
                test_array[:,-1]
                )
            
            models = {
                 "Linear Regression": LinearRegression(),
                 "K-Neighbors Regressor": KNeighborsRegressor(),
                 "Decision Tree": DecisionTreeRegressor(),
                 "Gradient Boosting": GradientBoostingRegressor(),
                 "Random Forest Regressor": RandomForestRegressor(),
                 "XGBRegressor": XGBRegressor(), 
                 "CatBoosting Regressor": CatBoostRegressor(verbose=False),
                 "AdaBoost Regressor": AdaBoostRegressor()
                   }
            
            params={
                "Linear Regression":{},
                "K-Neighbors Regressor":{
                                        "n_neighbors": [3, 5, 7],  # Test different values for the number of neighbors.
                                        "leaf_size": [10, 20, 30],  # Test different leaf sizes.
                                        "metric": ["euclidean", "manhattan"]  # Test different distance metrics.
                                        },
                "Decision Tree": {
                    'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                    # 'splitter':['best','random'],
                    # 'max_features':['sqrt','log2'],
                },
                
                "Gradient Boosting":{
                    # 'loss':['squared_error', 'huber', 'absolute_error', 'quantile'],
                    'learning_rate':[.1,.01,.05,.001],
                    'subsample':[0.6,0.7,0.75,0.8,0.85,0.9],
                    # 'criterion':['squared_error', 'friedman_mse'],
                    # 'max_features':['auto','sqrt','log2'],
                    'n_estimators': [8,16,32,64,128,256]
                },

                "Random Forest Regressor":{
                    # 'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                 
                    # 'max_features':['sqrt','log2',None],
                    'n_estimators': [8,16,32,64,128,256]
                },
                
                "XGBRegressor":{
                    'learning_rate':[.1,.01,.05,.001],
                    'n_estimators': [8,16,32,64,128,256]
                },
                "CatBoosting Regressor":{
                    'depth': [6,8,10],
                    'learning_rate': [0.01, 0.05, 0.1],
                    'iterations': [30, 50, 100]
                },
                "AdaBoost Regressor":{
                    'learning_rate':[.1,.01,0.5,.001],
                    # 'loss':['linear','square','exponential'],
                    'n_estimators': [8,16,32,64,128,256]
                }
                
            }

            model_report:dict=evaluate_model(X_train=X_train,y_train=y_train,X_test=X_test,y_test=y_test,
                                             models=models,param=params)
            
            #model_report:dict=evaluate_model(X_train=X_train,y_train=y_train, X_test=X_test, y_test=y_test,models=models)
            
            #to get the best model score from dict
            best_model_score=max(sorted(list(model_report.values())))

            # Get the best model name
            best_model_name=list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
                ]
            best_model=models[best_model_name]
            print("best model is:",best_model_name)

            if best_model_score<0.6:
                raise CustomException("No best model found")
            logging.info(f"best model found on both the training and testing datasets")

            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model)
            
            predicted=best_model.predict(X_test)
            r2_score_value=r2_score(y_test,predicted)
            return r2_score_value


        except Exception as e:
            raise CustomException(e,sys)  
    
     