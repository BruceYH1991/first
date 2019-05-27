import pandas as pd
import pymysql

mysql_config = {
    'host': 'cashlending-readonly.c3dsrzz0nv8o.ap-southeast-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'cashlending',
    'password': 'cash123456',
    'db': 'cashlending',
    'charset': 'utf8'
}

con = pymysql.Connect(**mysql_config)


sql = 'select cpi.merber_id, lai.id, cpi.formatted_number \
    from contact_person_info cpi left join loan_application_info lai \
    on cpi.merber_id = lai.member_id \
    where lai.application_time >20190520 and lai.application_time < 20190527 \
    and lai.is_older = 0 '

data = pd.read_sql(sql, con)

data.to_csv('contact.csv')
