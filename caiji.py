
import pandas as pd
import pymysql
from sys import argv


mysql_config = {
    'host': 'cashlending-readonly.c3dsrzz0nv8o.ap-southeast-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'cashlending',
    'password': 'cash123456',
    # 'db': 'cashlending',
    'charset': 'utf8'
}

data_note = int(argv[1])

con = pymysql.Connect(**mysql_config)

application_sql = 'select lai.id,\
    lai.member_id,\
    lai.geographical_location,\
    loi.status \
    from cashlending.loan_application_info lai left join \
    cashlending.loan_order_info loi \
    on lai.id = loi.application_id \
    where lai.is_older = 0 and lai.application_time > {}'

td_sql = 'select application_id,td_device_id,td_wifiip,td_wifimac \
    from indicator.etl_tongdun \
    where application_id in \
    (select id from cashlending.loan_application_info where \
    is_older = 0 and application_time > {})'

device_sql = 'select member_id,device_id \
    from cashlending.member_device_mapping \
    where member_id in \
    (select member_id from cashlending.loan_application_info where \
    is_older = 0 and application_time > {})'

mac_sql = 'select member_id,mac \
    from cashlending.member_device_track \
    where member_id in \
    (select member_id from cashlending.loan_application_info where \
    is_older = 0 and application_time > {})'

imei_sql = 'select device_id,android_imei \
    from cashlending.device_info \
    where device_id in \
    (select device_id from cashlending.member_device_mapping \
    where member_id in \
    (select member_id from cashlending.loan_application_info where \
    is_older = 0 and application_time > {}))'

contact_sql = 'select merber_id as member_id\
    from cashlending.contact_person_info \
    where merber_id in \
    (select member_id from cashlending.loan_application_info where \
    is_older = 0 and application_time > {}) \
    group by merber_id'

app_sql = 'select member_id from cashlending.personal_app_installed_record \
    where member_id in \
    (select member_id from cashlending.loan_application_info where \
    is_older = 0 and application_time > {}) \
    group by member_id'

yitu_sql = 'select lai.id as application_id, lbi.resemblance_status \
    from cashlending.loan_application_info lai left join \
    cashlending.loan_basis_info lbi on lai.loan_basis_info_id = lbi.id \
    where lai.is_older = 0 and lai.application_time > {}'

baidu_sql = 'select lai.id as application_id, lfp.score \
    from cashlending.loan_application_info lai left join \
    cashlending.loan_face_photo lfp \
    on lai.loan_basis_info_id = lfp.loan_basis_info_id \
    where lai.is_older = 0 and lai.application_time > {}'


def get_data(sql):
    data = pd.read_sql(sql.format(data_note), con)
    return data


application = get_data(application_sql)
application['geographical_location'].fillna(0, inplace=True)
application['LBS'] = application['geographical_location'].apply(
    lambda x: 1 if x else 0
)
application['order'] = application['status'].apply(
    lambda x: 1 if x >= 0 else 0
)
application.drop(['geographical_location', 'status'], axis=1, inplace=True)
application.rename(columns={'id': 'application_id'}, inplace=True)


def if_has(v):
    result = 1
    if v == '0.0.0.0' or v == 'None' or v == 'null' or v == 0:
        result = 0

    return result


td = get_data(td_sql)

for col in ['td_device_id', 'td_wifiip', 'td_wifimac']:
    td[col] = td[col].apply(if_has)


device = get_data(device_sql)
mac = get_data(mac_sql)
imei = get_data(imei_sql)

contact = get_data(contact_sql)
app = get_data(app_sql)

yitu = get_data(yitu_sql)
baidu = get_data(baidu_sql)


con.close()


device.drop_duplicates(subset='member_id', inplace=True)
mac.drop_duplicates(subset='member_id', inplace=True)
imei.drop_duplicates(subset='device_id', inplace=True)

device = device.merge(mac, how='left', left_on='member_id',
                      right_on="member_id")
device = device.merge(imei, how='left', on='device_id')


contact['contact'] = 1
app['app'] = 1

yitu.fillna(0, inplace=True)
yitu['yitu'] = yitu['resemblance_status'].apply(
    lambda x: 0 if isinstance(x, (int, float)) or x == 'None' else 1
)
yitu.drop(['resemblance_status'], axis=1, inplace=True)
baidu.fillna('n', inplace=True)
baidu['baidu'] = baidu['score'].apply(
    lambda x: 1 if isinstance(x, (int, float)) else 0
)
baidu.drop(['score'], axis=1, inplace=True)


data = application.merge(td, how='left', left_on='application_id',
                         right_on='application_id')
data = data.merge(device, how='left', on='member_id')
data = data.merge(contact, how='left', on='member_id')
data = data.merge(app, how='left', on='member_id')
data = data.merge(yitu, how='left', on='application_id')
data = data.merge(baidu, how='left', on='application_id')


data.fillna(0, inplace=True)


for col in ['device_id', 'mac', 'android_imei']:
    data[col] = data[col].apply(if_has)


passed = data[data['order'] == 1].copy()
passed.drop(['application_id', 'member_id', 'order'], axis=1, inplace=True)
data.drop(['application_id', 'member_id', 'order'], axis=1, inplace=True)


pass_len = passed.shape[0]
all_len = data.shape[0]

data_finish = data.sum()
pass_finish = passed.sum()

data_df = pd.DataFrame(data_finish)
pass_df = pd.DataFrame(pass_finish)

data_df.rename(columns={0: '采集数'}, inplace=True)
data_df['采集率'] = data_df['采集数'] / all_len
pass_df.rename(columns={0: '采集数'}, inplace=True)
pass_df['采集率'] = pass_df['采集数'] / pass_len


writer = pd.ExcelWriter('../采集情况_{}.xlsx'.format(data_note))
data_df.to_excel(writer, sheet_name='申请')
pass_df.to_excel(writer, sheet_name='通过')
writer.save()















