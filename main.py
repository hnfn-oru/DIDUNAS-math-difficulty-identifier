# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd
import numpy as np
from flask_cors import CORS
import logging

logging.getLogger('flask_cors').level = logging.DEBUG

class HybridEnsembleModel:
    def __init__(self, classifier, regressor):
        self.classifier = classifier
        self.regressor = regressor

    def hybrid_prediction(self, X_test):
        if X_test.shape[1] < 2:
            y_flag = self.classifier.predict(X_test.reshape([1, 10]))
            yhat = self.regressor.predict(X_test.reshape([1, 10]))

            if y_flag > 0 and yhat < 0.25:
                yhat = np.sqrt(yhat)
            if y_flag < 1 and yhat > 0.25:
                yhat = yhat * yhat

        else:
            y_flag = self.classifier.predict(X_test)
            yhat = self.regressor.predict(X_test)

            for count, value in enumerate(y_flag):
                if value > 0 and yhat[count] < 0.25:
                    yhat[count] = np.sqrt(yhat)
                if value < 1 and yhat[count] >= 0.25:
                    yhat[count] = yhat[count] * yhat[count]

        return y_flag, yhat

model = pickle.load(open('DIDUNAS_regression_model202305.pkl','rb'))

app=Flask(__name__)

cors = CORS(app, resources={r"/api/*": {"origins": "https://madita.vercel.app"}})

@app.route('/api/predict', methods=['POST'])
def predict():
    features_list = []
    features_list.append(request.form.get("quantities"))
    features_list.append(request.form.get("quantityComparison"))
    features_list.append(request.form.get("numberComparison"))
    features_list.append(request.form.get("colorPattern"))
    features_list.append(request.form.get("numberPattern"))
    features_list.append(request.form.get("hiddenNumber"))
    features_list.append(request.form.get("numberLine"))
    features_list.append(request.form.get("completionToTen"))
    features_list.append(request.form.get("plus"))
    features_list.append(request.form.get("minus"))

    features = np.array(features_list).reshape([1,10])
    predict_RMD, predict_pValue = model.hybrid_prediction(features) #note that here both Y/N predciton and a P-value predciotion are made.

    if predict_RMD>0:
        RMD='T'
    else:
        RMD='F'

    return {"prediction": RMD}


if __name__ == "__main__":
    app.run(port=8000,debug = False)
