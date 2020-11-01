#! /usr/bin/env python3
import json
import os
import sys
import time
from concurrent import futures
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from fbprophet import Prophet

import ServerSideExtension_pb2 as SSE
import grpc


class QlikService(SSE.ConnectorServicer):

    def __init__(self, funcdef_file):
        self._function_definitions = funcdef_file
        print('Logging enabled')

    @property
    def function_definitions(self):
        return self._function_definitions

    @property
    def functions(self):
        return {
            0: '_linearRegression',
            1: '_Prophet',
            2: '_ProphetExtract',
        }

    @staticmethod
    def _get_function_id(context):
        metadata = dict(context.invocation_metadata())
        header = SSE.FunctionRequestHeader()
        header.ParseFromString(metadata['qlik-functionrequestheader-bin'])
        return header.functionId

    @staticmethod
    def _linearRegression(request, context):

        print('\n********** LinearRegression Invoked **********')


        df = pd.DataFrame([(row.duals[0].numData) \
                          for request_rows in request \
                          for row in request_rows.rows ] \
                          ,columns=['y'])

        print('\n****** Qlik Request Data **********')
        print(df.head())

        X = pd.Series(range(0,len(df)))
        reg = LinearRegression().fit( X.values.reshape(-1,1) \
                           ,df['y'])

        print('\n********** Fitting Linear Regression Model **********')

        yhat = reg.coef_ * X + reg.intercept_

        print("coefficient : %.4f" %reg.coef_[0])
        print("intercept : %.4f" %reg.intercept_)

        duals = iter([[SSE.Dual(numData=d)] for d in yhat])
        yield SSE.BundledRows(rows=[SSE.Row(duals=d) for d in duals])


    @staticmethod
    def _Prophet(request, context):

        df = pd.DataFrame([ (row.duals[1].numData, row.duals[0].numData) \
                        for request_rows in request \
                        for row in request_rows.rows ] \
                        ,columns = ['ds', 'y'])

        df['ds'] = pd.to_datetime( df['ds'] ,unit = 'D' ,origin = pd.Timestamp('1899-12-30'))

        df.drop(df.tail(12).index,inplace = True)

        model = Prophet().fit(df)
        future_data = model.make_future_dataframe(periods=12, freq = 'm')
        future_data = model.predict(future_data)

        #print(future_data[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

        duals = iter([[SSE.Dual(numData=d)] for d in future_data['yhat']])
        yield SSE.BundledRows(rows=[SSE.Row(duals=d) for d in duals])


    @staticmethod
    def _ProphetExtract(request, context):

        df = pd.DataFrame([ (row.duals[1].numData, row.duals[0].numData) \
                        for request_rows in request \
                        for row in request_rows.rows ] \
                        ,columns = ['ds', 'y'])
        df_orig = df[:]

        df['ds'] = pd.to_datetime( df['ds'] ,unit = 'D' ,origin = pd.Timestamp('1899-12-30'))
        df.drop(df.tail(36).index,inplace = True)

        model = Prophet().fit(df)
        future_data = model.make_future_dataframe(periods=36, freq = 'm')
        future_data = model.predict(future_data)

        #print(future_data.dtypes)
        #print(future_data)
        #print(len(future_data))

        dualsList = []
        dualsList.append([SSE.Dual(numData=d) for d in future_data['yhat']])
        dualsList.append([SSE.Dual(numData=d) for d in future_data['yhat_lower']])
        dualsList.append([SSE.Dual(numData=d) for d in future_data['yhat_upper']])
        dualsList.append([SSE.Dual(numData=d) for d in df_orig['ds']])
        dualsList.append([SSE.Dual(numData=d) for d in df_orig['y']])

        response_rows = []
        for i in range(len(df_orig)):
            duals = [dualsList[j][i] for j in range(len(dualsList))]
            response_rows.append(SSE.Row(duals = duals))

        #print(SSE.BundledRows(rows=response_rows))

        yield SSE.BundledRows(rows=response_rows)


    def GetCapabilities(self, request, context):
        print('GetCapabilities')
        capabilities = SSE.Capabilities(allowScript=False,
                                        pluginIdentifier='SSEPython',
                                        pluginVersion='v0.1')

        with open(self.function_definitions) as json_file:
            for definition in json.load(json_file)['Functions']:
                function = capabilities.functions.add()
                function.name = definition['Name']
                function.functionId = definition['Id']
                function.functionType = definition['Type']
                function.returnType = definition['ReturnType']

                for param_name, param_type in sorted(definition['Params'].items()):
                    function.params.add(name=param_name, dataType=param_type)

                print('Adding to capabilities: {}({})'.format(function.name,
                                                                     [p.name for p in function.params]))
        return capabilities

    def ExecuteFunction(self, request_iterator, context):
        func_id = self._get_function_id(context)
        print('ExecuteFunction (functionId: {})'.format(func_id))
        return getattr(self, self.functions[func_id])(request_iterator, context)

    def Serve(self, port):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        SSE.add_ConnectorServicer_to_server(self, server)

        server.add_insecure_port('[::]:{}'.format(port))
        print('*** Running server in insecure mode on port: {} ***'.format(port))

        server.start()
        try:
            while True:
                time.sleep(60*60)
        except KeyboardInterrupt:
            server.stop(0)


if __name__ == '__main__':

    def_file = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'function_definitions.json')

    Service = QlikService(def_file)
    Service.Serve('50052')
