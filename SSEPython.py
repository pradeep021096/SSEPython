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
from datetime import datetime

import ServerSideExtension_pb2 as SSE
import grpc

from pprint import pprint

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
            0: '_linearRegression'
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
                          ,columns=['Y'])

        print('\n****** Qlik Request Data **********')
        print(df.head())

        X = pd.Series(range(0,len(df)))
        reg = LinearRegression().fit( X.values.reshape(-1,1) \
                           ,df['Y'])

        print('\n********** Fitting Linear Regression Model **********')

        yhat = reg.coef_ * X + reg.intercept_

        print("coefficient : %.4f" %reg.coef_[0])
        print("intercept : %.4f" %reg.intercept_)

        duals = iter([[SSE.Dual(numData=d)] for d in yhat])
        yield SSE.BundledRows(rows=[SSE.Row(duals=d) for d in duals])

    def GetCapabilities(self, request, context):
        print('GetCapabilities')
        capabilities = SSE.Capabilities(allowScript=False,
                                        pluginIdentifier='MLPython',
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
