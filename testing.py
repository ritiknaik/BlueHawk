import requests
import pathlib
from threading import Thread

def create_arr_of_dict(filename):
    arr_of_req = []
    req = dict()
    req_line = ''
    with open(filename, 'r') as r:
        sep = True
        for line in r:
            if(line == '\n' and sep):
                sep = False
            elif(line == '\n' and not sep):
                sep = True
                arr_of_req.append([req_line,req])
                req = dict()
            else:
                values = line.split(': ')
                if(len(values) == 1):
                    method = values[0].split()[0]
                    uri = values[0].split()[1]
                    req_line = [method, uri]
                else:
                    key, value = values
                    req[key] = value[:-1]
    arr_of_req.pop(0)
    return arr_of_req

def validate(correct_status, received_status,received_response):
    f = open('results.txt','w')
    score = 0
    for i in received_status.keys():
        if(correct_status[i] == received_status[i]):
            score += 1
            print('Test case %s passed! score %s' % (i, score))
            f.write(str(i) + '-- Expected: ' + str(correct_status[i]) + ' Received: ' + str(received_status[i]) + '\n')
            f.write(str(received_response[i].headers) + '\n')
        else:
            print('Test case %s failed score %s' % (i, score))
            f.write(str(i) + '-- Expected: ' + str(correct_status[i]) + ' Received: ' + str(received_status[i]) + ' Reason: ' + received_response[i].reason + '\n')
            f.write(str(received_response[i].headers) + '\n')
    return score

def send_req(all_req):
    received_status = dict()
    received_response = dict()
    for i in range(len(all_req)):
        # print(i)
        req_line = all_req[i][0]
        method = req_line[0]
        uri = req_line[1]
        req_headers = all_req[i][1]
        url = 'http://127.0.0.1:8000' + uri
        if(method == 'GET'):
            # print('get',url, req_headers)
            resp = requests.get(url, headers=req_headers)
        elif(method == 'HEAD'):
            # print('head',url, req_headers)
            resp = requests.head(url, headers=req_headers)
        elif(method == 'POST'):
            # print('post',url, req_headers)
            if(len(uri.split('.')) > 1):
                file = {'media': open(abs_path + '/resources' + uri, 'rb')}
            else:
                file = {'media': open(abs_path + '/resources' + uri + '/index.html', 'rb')}
            resp = requests.post(url, headers=req_headers,files=file)
        elif(method == 'PUT'):
            # print('put',url, req_headers)
            if(len(uri.split('.')) > 1):
                file = {'media': open(abs_path + '/resources' + uri, 'rb')}
            else:
                file = {'media': open(abs_path + '/resources' + uri + '/index.html', 'rb')}
            resp = requests.put(url, headers=req_headers,files=file)
        elif(method == 'DELETE'):
            # print('delete',url, req_headers)
            resp = requests.delete(url, headers=req_headers)
        elif(method == 'PATCH'):
            resp = requests.patch(url, headers=req_headers)
        elif(method == 'OPTIONS'):
            resp = requests.options(url, headers=req_headers)
        else:
            pass
        received_response[i] = resp
        received_status[i] = resp.status_code
    return received_response, received_status

def send_one_req(method, req_headers, uri, corr_status, j):
    try:
        url = 'http://127.0.0.1:8000' + uri
        if(method == 'GET'):
            # print('get',url, req_headers)
            resp = requests.get(url, headers=req_headers)
        elif(method == 'HEAD'):
            # print('head',url, req_headers)
            resp = requests.head(url, headers=req_headers)
        elif(method == 'POST'):
            # print('post',url, req_headers)
            if(len(uri.split('.')) > 1):
                file = {'media': open(abs_path + '/resources' + uri, 'rb')}
            else:
                file = {'media': open(abs_path + '/resources' + uri + '/index.html', 'rb')}
            resp = requests.post(url, headers=req_headers,files=file)
        elif(method == 'PUT'):
            # print('put',url, req_headers)
            if(len(uri.split('.')) > 1):
                file = {'media': open(abs_path + '/resources' + uri, 'rb')}
            else:
                file = {'media': open(abs_path + '/resources' + uri + '/index.html', 'rb')}
            resp = requests.put(url, headers=req_headers,files=file)
        elif(method == 'DELETE'):
            # print('delete',url, req_headers)
            resp = requests.delete(url, headers=req_headers)
        else:
            print('Test case %s of multi threaded failed!' % j)
            return
        if(corr_status == resp.status_code):
            print('Test case %s of multi threaded passed!' % j)
    except Exception as e:
        print(e)
    return


filename = 'request.txt'
abs_path = str(pathlib.Path().absolute())
# try:
all_req = create_arr_of_dict(filename)
correct_status = {0 : 200,
                1 : 200,
                2 : 200,
                3 : 200,
                4 : 200,
                5 : 200,
                6 : 200,
                7 : 406,
                8 : 404,
                9 : 200,
                10 : 304,
                11 : 200,
                12 : 412,
                13 : 200,##
                14 : 412,
                15 : 403,
                16 : 405,
                17 : 201,
                18 : 201,
                19 : 400,
                20 : 405,
                21 : 404,
                22 : 200,
                23 : 201,
                24 : 501,
                25 : 501,
                26 : 501,
                27 : 200,###
                28 : 416,
                29 : 200,
                30 : 200,
                31 : 200,
                32 : 200,
                33 : 200,
                34 : 200,
                35 : 200,
                36 : 200,
                37 : 200,
                38 : 200,
                39 : 406,
                40 : 200,
                41 : 200,
                42 : 200,
                43 : 406,
                44 : 200,
                45 : 200,
                46 : 200,
                47 : 200,
                48 : 201,
                49 : 200}

received_response, received_status = send_req(all_req)
score = validate(correct_status, received_status,received_response)
print('%s out of %s Test cases passed!' % (score, len(correct_status)))

req_for_multi = all_req[:10]
# print(req_for_multi)
try: 
    for i in range(10):
        mreq_line = req_for_multi[i][0]
        mmethod = mreq_line[0]
        muri = mreq_line[1]
        mreq_headers = req_for_multi[i][1]
        corr_status = correct_status[i]
        t=Thread(target=send_one_req, args=(mmethod, mreq_headers, muri, corr_status, i,))
        t.start()
except Exception as e:
    print(e)


