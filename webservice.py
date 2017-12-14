#!/usr/bin/env python
import psycopg2
 
from DBUtils.PersistentDB import PersistentDB
 
from spyne import Application, rpc, ServiceBase, Integer, Boolean
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

import logging
from wsgiref.simple_server import make_server

### TODO: refactor with Flaskr

persist = PersistentDB(psycopg2, 1000,
                       host='localhost',
                       database='exness',
                       user='burmashev',
                       password='exness_test')


class RelationCheckService(ServiceBase):

    @rpc(Integer, Integer, _returns=Boolean)
    def is_users_related(self, user_a, user_b):
        """Checks if user_a is related to user_b.
 
        Relation between users means they've shared at least two IP-addresses from different /24 networks.
 
        @param user_a id of user
        @param user_b id of another user
        @return boolean value representing if there is a relation between user_a and user_b
        """
        connection = persist.connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT is_users_related(%s, %s)", (user_a, user_b))
            result = cursor.fetchone()[0]
            if result:
                cursor.execute("SELECT save_relation(%s, %s)", (user_a, user_b))
                connection.commit()
            cursor.close()
            return result
        finally:
            connection.close()
 
 
application = Application([RelationCheckService],
                          'exness.test',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())
 
wsgi_application = WsgiApplication(application)

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    logging.info("listening to http://127.0.0.1:8080")
    logging.info("wsdl is at: http://localhost:8080/?wsdl")

    server = make_server('127.0.0.1', 8080, wsgi_application)
    server.serve_forever()