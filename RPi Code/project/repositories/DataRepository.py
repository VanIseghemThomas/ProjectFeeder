from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    #--------Methods van feederDB-----------
    #READ
    @staticmethod
    def read_logs():
        sql = "SELECT * from tbllogs order by timestamp desc"
        return Database.get_rows(sql)

    @staticmethod
    def read_measurements():
        sql = "select * from vw_measurements order by timestamp desc"
        return Database.get_rows(sql)

    @staticmethod
    def read_measurements_with_id(id):
        if id != None:
            sql = "select * from vw_measurements where sensorid = %s order by timestamp desc "
            params = [id]
        else:
            print('No ID given')
        return Database.get_rows(sql, params)
    
    @staticmethod
    def read_actuator_events():
        sql = "SELECT * from vw_actuator_events order by timestamp desc"
        return Database.get_rows(sql)

    @staticmethod
    def read_actuators():
        sql = "SELECT * from tblactuators"
        return Database.get_rows(sql)

    @staticmethod
    def read_sensors():
        sql = "SELECT * from tblsensors"
        return Database.get_rows(sql)

    @staticmethod
    def read_presets():
        sql = "SELECT * from tblpresets"
        return Database.get_rows(sql)
    
    #ADD
    @staticmethod
    def add_actuator_event(timestamp, value, unit, actuatorid, presetid=None):
        #actuatorid check because database allows null value in table
        if(actuatorid != None):
            sql = "INSERT INTO tbllogs(timestamp, value, unit, actuatorid, presetid) VALUES(%s,%s,%s,%s,%s)"
            params = [timestamp, value, unit, actuatorid, presetid]
            return Database.execute_sql(sql, params)
        else:
            return "No actuator ID"

    @staticmethod
    def add_measurement(timestamp, value, unit, sensorid):
        #sensorid check because database allows null value in table
        if(sensorid != None):
            sql = "INSERT INTO tbllogs(timestamp, value, unit, sensorid) VALUES(%s,%s,%s,%s)"
            params = [timestamp, value, unit, sensorid]
            return Database.execute_sql(sql, params)
        else:
            return "No sensor ID"

    @staticmethod
    def add_preset(dayofweek, hour, minute, amount):
        sql = "INSERT INTO tblpresets(dayofweek, hour, minute, amount) VALUES(%s,%s,%s,%s)"
        print('add preset')
        params = [dayofweek, hour, minute, amount]
        return Database.execute_sql(sql, params)

    #DELETE
    @staticmethod
    def delete_preset(idpreset):
        sql = "DELETE from tblpresets WHERE presetid = %s"
        params = [idpreset]
        return Database.execute_sql(sql, params)

    #-------Methods van basis IOT chain-------
    @staticmethod
    def read_status_lampen():
        sql = "SELECT * from lampen"
        return Database.get_rows(sql)

    @staticmethod
    def read_status_lamp_by_id(id):
        sql = "SELECT * from lampen WHERE id = %s"
        params = [id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def update_status_lamp(id, status):
        sql = "UPDATE lampen SET status = %s WHERE id = %s"
        params = [status, id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_status_alle_lampen(status):
        sql = "UPDATE lampen SET status = %s"
        params = [status]
        return Database.execute_sql(sql, params)
