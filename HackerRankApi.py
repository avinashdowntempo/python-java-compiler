from pymongo import MongoClient
from flask import Flask, jsonify, request
from bson.json_util import dumps
from flask_cors import CORS
import datetime
import json
import subprocess
import os
from subprocess import check_output

app = Flask(__name__)
CORS(app)


def connection():
    client = MongoClient(host='192.168.100.166', port=27017)
    # client = MongoClient( port=27017)
    db = client['HackerRankerDB']
    return db


@app.route('/codearea', methods=['POST'])
def codeArea():
    code = request.json
    date = datetime.date.today()
    try:
        db = connection()
        posts = db.HR_ValidateCode
        post_id = posts.insert_one({"VC_userid": "usr016", "VC_QID": 16, "VC_Submitted_code": code["codearea"],
                                    "VC_created_date": date.strftime("%B %d, %Y"), "VC_Status": "submitted",
                                    "VC_interviewerID": "int001", "VC_InterviewerComments": "good",
                                    "VC_ReviewerID": "rev01", "VC_ReviewerComments": "very Good"}).inserted_id
        post_id
        return jsonify({'data': code})

    except Exception as e:
        print(str(e))


@app.route('/interviewer', methods=['GET'])
def getInterviewerDtls():
    try:
        db = connection()
        data = dumps(db["HR_ValidateCode"].find({"VC_Status": "submitted"}))
        return data


    except Exception as e:
        print(str(e))


@app.route('/run', methods=['POST'])
def getJavaRun():
    data = request.data
    dataDict = json.loads(data)
    userid = dataDict["userid"]
    for file in os.listdir("."):
        if file.endswith(".class"):
            classFile = file
            print(os.path.splitext(classFile)[0])

    cmd = r'"java" ' + os.path.splitext(classFile)[0]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode('utf-8'))
        print(result.stderr.decode('utf-8'))
        if result.stderr.decode('utf-8') is '':
            print("Executed successfully")
            db = connection()
            db.HR_ValidateCode.update_one(
                {"VC_userid": userid},
                {
                    "$set": {
                        "VC_ExecutedResult": result.stdout.decode('utf-8')
                    }
                }
            )
            os.remove("test.java")
            for file in os.listdir("."):
                if file.endswith(".class"):
                    os.remove(file)
                    print(file)
                    print("File Removed!")
        else:
            print("Executions failed")
            os.remove("test.java")
            # os.remove("test.class")
            for file in os.listdir("."):
                if file.endswith(".class"):
                    print(file)
                    os.remove(file)
                    print("File Removed!")
    except Exception as e:
        print(str(e))

    return jsonify({'data': result.stdout.decode('utf-8')})


@app.route('/compile', methods=['POST'])
def compile_java():
    data = request.data
    dataDict = json.loads(data)
    print(dataDict["code"])
    userid = dataDict["userid"]
    print(userid)
    f = open("test.java", "w+")
    f.write(dataDict["code"])
    f.close()
    cmd = r'"javac" ' + "test.java"
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # result.stdout.decode('utf-8')
        print(result.stderr.decode('utf-8'))
        if result.stderr.decode('utf-8') is '':
            print("Compilation sucess")
            db = connection()
            db.HR_ValidateCode.update_one(
                {"VC_userid": userid},
                {
                    "$set": {
                        "VC_CompilationResult": "Success"
                    }
                }
            )
        else:
            print("Compilation failed")
            os.remove("test.java")

            print("File Removed!")
            db = connection()
            db.HR_ValidateCode.update_one(
                {"VC_userid": userid},
                {
                    "$set": {
                        "VC_CompilationResult": result.stderr.decode('utf-8')
                    }
                }
            )

    except Exception as e:
        print(str(e))

    return jsonify({'data': result.stderr.decode('utf-8')})


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=9080)
