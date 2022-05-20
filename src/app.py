from flask import Flask,render_template,request,redirect,session
from web3 import Web3,HTTPProvider
import json

def connect_Blockchain_drug(acc):
    blockchain_address="http://127.0.0.1:8545"
    web3=Web3(HTTPProvider(blockchain_address))
    if(acc==0):
        acc=web3.eth.accounts[0]
    web3.eth.defaultAccount=acc
    artifact_path='../build/contracts/drug.json'
    contract_address="0x2f07588132decdA0020E46Fb9579d265D86219e1"
    with open(artifact_path) as f:
        contract_json=json.load(f)
        contract_abi=contract_json['abi']

    contract=web3.eth.contract(address=contract_address,abi=contract_abi)
    print('connected with blockchain')
    return (contract,web3)

def connect_Blockchain_register(acc):
    blockchain_address="http://127.0.0.1:8545"
    web3=Web3(HTTPProvider(blockchain_address))
    if(acc==0):
        acc=web3.eth.accounts[0]
    web3.eth.defaultAccount=acc
    artifact_path='../build/contracts/register.json'
    contract_address="0xD1efA8201c4d894F9eBdD96d7FeDb85fDccfcc1C"
    with open(artifact_path) as f:
        contract_json=json.load(f)
        contract_abi=contract_json['abi']

    contract=web3.eth.contract(address=contract_address,abi=contract_abi)
    print('connected with blockchain')
    return (contract,web3)

app=Flask(__name__)
app.secret_key='makeskilled'

@app.route('/')
def indexPage():
    return render_template('index.html')

@app.route('/register')
def registerPage():
    return render_template('register.html')

@app.route('/login')
def loginPage():
    return render_template('login.html')

@app.route('/registerUser',methods=['GET','POST'])
def registerUser():
    name=request.form['name']
    role=int(request.form['role'])
    walletaddr=request.form['walletaddr']
    password=int(request.form['password'])
    print(walletaddr,password,name,role)
    contract,web3=connect_Blockchain_register(walletaddr)
    tx_hash=contract.functions.registerUser(walletaddr,password,name,role).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/login')

@app.route('/loginUser',methods=['GET','POST'])
def loginUser():
    walletaddr=request.form['walletaddr']
    password=int(request.form['password'])
    print(walletaddr,password)
    contract,web3=connect_Blockchain_register(walletaddr)
    state=contract.functions.loginUser(walletaddr,password).call()
    print(state)
    if(state==True):
        session['walletaddr']=walletaddr
        contract,web3=connect_Blockchain_register(walletaddr)
        _users,_passwords,_roles,_names=contract.functions.viewUsers().call()
        userIndex=_users.index(walletaddr)
        role=_roles[userIndex]
        print(role)
        if(role==1):
            return redirect('/labdashboard')
        elif(role==2):
            return redirect('/manudashboard')
        elif(role==3):
            return redirect('/waremdashboard')
        elif(role==4):
            return redirect('/transdashboard')
        elif(role==5):
            return redirect('/waretdashboard')
        elif(role==6):
            return redirect('/hospitalsdashboard')
        elif(role==7):
            return redirect('/retailersdashboard')
    else:
        return redirect('/login')

@app.route('/labdashboard')
def labDashboard():
    return render_template('labdashboard.html')

@app.route('/manudashboard')
def manudashboard():
    walletaddr=session['walletaddr']
    contract,web3=connect_Blockchain_register(0)
    _users,_passwords,_roles,_names=contract.functions.viewUsers().call()

    contract,web3=connect_Blockchain_drug(walletaddr)
    _lab,_labmanu,_labform=contract.functions.viewLabManufacturers().call()
    data=[]
    for i in range(len(_labform)):
        dummy=[]
        if(_labmanu[i]==walletaddr):
            dummy.append(_labform[i])
            dummy.append(_lab[i])
            labindex=_users.index(_lab[i])
            dummy.append(_names[labindex])
        data.append(dummy)
    print(data)
    l=len(data)
    return render_template('manudashboard.html',len=l,dashboard_data=data)

@app.route('/waremdashboard')
def waremdashboard():
    contract,web3=connect_Blockchain_register(0)
    _users,_passwords,_roles,_names=contract.functions.viewUsers().call()

    contract,web3=connect_Blockchain_drug(0)
    _lotmanu,_lotid,_lotpillcount,_lotlabform,_lotstatus=contract.functions.viewLots().call()

    contract,web3=connect_Blockchain_drug(session['walletaddr'])
    _lotmanuwarehousem,_lotwarehousem,_lotidwarehousem=contract.functions.viewLotWareM().call()
    _waremtransport,_transporters,_warettransport,_transportStatus,_lotidtransport=contract.functions.viewTransport().call()
    data=[]
    for i in range(len(_lotidwarehousem)):
        if _lotwarehousem[i]==session['walletaddr']:
            dummy=[]
            userIndex=_users.index(_lotmanuwarehousem[i])
            dummy.append(_names[userIndex])
            dummy.append(_lotmanuwarehousem[i])
            dummy.append(_lotidwarehousem[i])
            labformIndex=_lotid.index(_lotidwarehousem[i])
            dummy.append(_lotlabform[labformIndex])
            dummy.append(_lotpillcount[labformIndex])
            
            try:
                lotstatusIndex=_lotidtransport.index(_lotidwarehousem[i])
                if _transportStatus[lotstatusIndex]==0:
                    dummy.append('In-Transit')
                else:
                    dummy.append('Delivered')
            except:
                dummy.append('Available')

            data.append(dummy)
    l=len(data)
    return render_template('waremdashboard.html',len=l,dashboard_data=data)

@app.route('/hospitalsdashboard')
def hospitalsdashboard():
    return render_template('hospitalsdashboard.html')

@app.route('/retailersdashboard')
def retailersdashboard():
    return render_template('retailersdashboard.html')

@app.route('/logout')
def logout():
    session['walletaddr']=''
    return redirect('/')

@app.route('/shareFormula',methods=['POST','GET'])
def shareFormula():
    walletaddr=request.form['walletaddr']
    mformula=request.form['mformula']
    print(walletaddr,mformula)
    contract,web3=connect_Blockchain_drug(walletaddr)
    tx_hash=contract.functions.addLabManufacturer(session['walletaddr'],walletaddr,mformula).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/viewlabmanufacturers')

@app.route('/viewlabmanufacturers')
def viewlabmanufacturers():
    contract,web3=connect_Blockchain_register(0)
    _users,_passwords,_roles,_names=contract.functions.viewUsers().call()

    contract,web3=connect_Blockchain_drug(session['walletaddr'])
    _lab,_labmanu,_labform=contract.functions.viewLabManufacturers().call()
    data=[]
    for i in range(len(_labmanu)):
        dummy=[]
        dummy.append(_labmanu[i])
        userIndex=_users.index(_labmanu[i])
        dummy.append(_names[userIndex])
        dummy.append(_labform[i])
        data.append(dummy)
    print(data)
    l=len(data)
    return render_template('viewlabmanufacturers.html',len=l,dashboard_data=data)

@app.route('/viewFeedbackslab')
def viewFeedbackslab():
    contract,web3=connect_Blockchain_register(0)
    _users,_passwords,_roles,_names=contract.functions.viewUsers().call()

    contract,web3=connect_Blockchain_drug(session['walletaddr'])
    _lab,_labmanu,_labform=contract.functions.viewLabManufacturers().call()
    _labfeeds=contract.functions.viewLabFeedback().call()
    data=[]
    for i in range(len(_labfeeds)):
        for j in range(len(_labfeeds[i])):
            dummy=[]
            dummy.append(_labform[i])
            dummy.append(_labfeeds[i][j])
            userIndex=_users.index(_labmanu[i])
            dummy.append(_names[userIndex])
            data.append(dummy)
    print(data)
    l=len(data)
    return render_template('viewFeedbackslab.html',len=l,dashboard_data=data)

@app.route('/createlot')
def createlot():
    contract,web3=connect_Blockchain_drug(session['walletaddr'])
    _lab,_labmanu,_labform=contract.functions.viewLabManufacturers().call()
    data=[]
    for i in range(len(_labform)):
        dummy=[]
        if(_labmanu[i]==session['walletaddr']):
            dummy.append(_labform[i])
        data.append(dummy)
    return render_template('createlot.html',len1=len(data),dashboard_data1=data)

@app.route('/createlotform',methods=['POST','GET'])
def createlotform():
    lotmanu=session['walletaddr']
    lotid=int(request.form['lotid'])
    lotpillcount=int(request.form['lotpillcount'])
    lotlabform=request.form['lotlabform']
    print(lotmanu,lotid,lotpillcount,lotlabform)
    contract,web3=connect_Blockchain_drug(lotmanu)
    tx_hash=contract.functions.createLot(lotmanu,lotid,lotpillcount,lotlabform).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/viewlots')

@app.route('/viewlots')
def viewlots():
    contract,web3=connect_Blockchain_register(0)
    _users,_passwords,_roles,_names=contract.functions.viewUsers().call()

    contract,web3=connect_Blockchain_drug(0)
    _lotmanu,_lotid,_lotpillcount,_lotlabform,_lotstatus=contract.functions.viewLots().call()
    print(_lotmanu,_lotid,_lotpillcount,_lotlabform,_lotstatus)
    data=[]
    for i in range(len(_lotid)):
        dummy=[]
        userIndex=_users.index(_lotmanu[i])
        dummy.append(_names[userIndex])
        dummy.append(_lotmanu[i])
        dummy.append(_lotid[i])
        dummy.append(_lotpillcount[i])
        dummy.append(_lotlabform[i])
        if(_lotstatus[i]==1):
            dummy.append('Available')
        else:
            dummy.append('Allocated')
        data.append(dummy)
    l=len(data)
    return render_template('viewlots.html',len=l,dashboard_data=data)

@app.route('/allocatewarehousem')
def allocatewarehousem():
    return render_template('allocatewarehousem.html')

@app.route('/allocatewarehousemform',methods=['POST','GET'])
def allocatewarehousemform():
    lotmanu=session['walletaddr']
    lotid=int(request.form['lotid'])
    lotwarem=request.form['lotwarem']
    print(lotmanu,lotid,lotwarem)
    contract,web3=connect_Blockchain_drug(lotmanu)
    tx_hash=contract.functions.allocateLotWareM(lotmanu,lotid,lotwarem).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/viewWarehousem')

@app.route('/viewWarehousem')
def viewWarehousem():
    contract,web3=connect_Blockchain_register(0)
    _users,_passwords,_roles,_names=contract.functions.viewUsers().call()

    contract,web3=connect_Blockchain_drug(0)
    _lotmanu,_lotid,_lotpillcount,_lotlabform,_lotstatus=contract.functions.viewLots().call()

    _lotmanuwarehousem,_lotwarehousem,_lotidwarehousem=contract.functions.viewLotWareM().call()
    print(_lotmanuwarehousem,_lotwarehousem,_lotidwarehousem)
    data=[]
    for i in range(len(_lotmanuwarehousem)):
        dummy=[]
        userIndex=_users.index(_lotmanuwarehousem[i])
        dummy.append(_names[userIndex])
        dummy.append(_lotmanuwarehousem[i])
        lotnameIndex=_lotid.index(_lotidwarehousem[i])
        dummy.append(_lotlabform[lotnameIndex])
        dummy.append(_lotidwarehousem[i])
        dummy.append(_lotpillcount[lotnameIndex])
        userIndex=_users.index(_lotwarehousem[i])
        dummy.append(_names[userIndex])
        dummy.append(_lotwarehousem[i])
        data.append(dummy)
    l=len(data)
    return render_template('viewWarehousem.html',len=l,dashboard_data=data)

@app.route('/scheduleTransport')
def scheduleTransport():
    return render_template('scheduleTransport.html')

@app.route('/scheduletransportform',methods=['GET','POST'])
def scheduletransportform():
    walletaddr=session['walletaddr']
    lotid=int(request.form['lotid'])
    lottransporter=request.form['lottransporter']
    lotwaret=request.form['lotwaret']
    print(walletaddr,lotid,lottransporter,lotwaret)
    contract,web3=connect_Blockchain_drug(walletaddr)
    tx_hash=contract.functions.createTransport(walletaddr,lottransporter,lotwaret,lotid).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/viewSchedules')

@app.route('/viewSchedules')
def viewSchedules():
    walletaddr=session['walletaddr']
    contract,web3=connect_Blockchain_register(0)
    _users,_passwords,_roles,_names=contract.functions.viewUsers().call()

    contract,web3=connect_Blockchain_drug(walletaddr)
    _waremtransport,_transporters,_warettransport,_transportStatus,_lotidtransport=contract.functions.viewTransport().call()
    data=[]
    for i in range(len(_lotidtransport)):
        if _waremtransport[i]==walletaddr:
            dummy=[]
            userIndex=_users.index(_transporters[i])
            dummy.append(_names[userIndex])
            dummy.append(_transporters[i])
            userIndex=_users.index(_warettransport[i])
            dummy.append(_names[userIndex])
            dummy.append(_warettransport[i])
            dummy.append(_lotidtransport[i])
            if(_transportStatus[i]==1):
                dummy.append("Delivered")
            else:
                dummy.append("In-transit")
            data.append(dummy)
    l=len(data)
    return render_template('viewSchedules.html',len=l,dashboard_data=data)

@app.route('/transdashboard')
def transdashboard():
    walletaddr=session['walletaddr']
    contract,web3=connect_Blockchain_register(0)
    _users,_passwords,_roles,_names=contract.functions.viewUsers().call()

    contract,web3=connect_Blockchain_drug(walletaddr)
    _waremtransport,_transporters,_warettransport,_transportStatus,_lotidtransport=contract.functions.viewTransport().call()

    data=[]
    for i in range(len(_lotidtransport)):
        if _transporters[i]==walletaddr:
            dummy=[]
            userIndex=_users.index(_waremtransport[i])
            dummy.append(_names[userIndex])
            dummy.append(_waremtransport[i])
            userIndex=_users.index(_warettransport[i])
            dummy.append(_names[userIndex])
            dummy.append(_warettransport[i])
            dummy.append(_lotidtransport[i])
            if(_transportStatus[i]==1):
                dummy.append("Delivered")
            else:
                dummy.append("In-transit")
            data.append(dummy)
    l=len(data)

    return render_template('transdashboard.html',len=l,dashboard_data=data)

@app.route('/updateTransport')
def updateTransport():
    return render_template('updateTransport.html')

@app.route('/updateTransportForm',methods=['GET','POST'])
def updateTransportForm():
    lotid=int(request.form['lotid'])
    transportStatus=int(request.form['transportStatus'])
    contract,web3=connect_Blockchain_drug(session['walletaddr'])
    tx_hash=contract.functions.updateTransport(lotid,transportStatus).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return(redirect('/transdashboard'))

@app.route('/waretdashboard')
def waretdashboard():
    walletaddr=session['walletaddr']
    contract,web3=connect_Blockchain_register(0)
    _users,_passwords,_roles,_names=contract.functions.viewUsers().call()

    contract,web3=connect_Blockchain_drug(walletaddr)
    _lotmanu,_lotid,_lotpillcount,_lotlabform,_lotstatus=contract.functions.viewLots().call()

    contract,web3=connect_Blockchain_drug(walletaddr)
    _waremtransport,_transporters,_warettransport,_transportStatus,_lotidtransport=contract.functions.viewTransport().call()

    data=[]
    for i in range(len(_warettransport)):
        if _warettransport[i]==walletaddr:
            dummy=[]
            waremIndex=_users.index(_waremtransport[i])
            dummy.append(_names[waremIndex])
            manuIndex=_lotid.index(_lotidtransport[i])
            manuwallet=_lotmanu[manuIndex]
            manuIndex=_users.index(manuwallet)
            dummy.append(_names[manuIndex])
            # dummy.append(_waremtransport[i])
            transportIndex=_users.index(_transporters[i])
            dummy.append(_names[transportIndex])
            # dummy.append(_transporters[i])
            lotIndex=_lotid.index(_lotidtransport[i])
            dummy.append(_lotidtransport[i])
            dummy.append(_lotlabform[lotIndex])
            dummy.append(_lotpillcount[lotIndex])
            if(_transportStatus[i]==0):
                dummy.append('In-Transit')
            else:
                dummy.append('Available')
            
            data.append(dummy)
    l=len(data)
    return render_template('waretdashboard.html',len=l,dashboard_data=data)

@app.route('/distributeHospitals')
def distributeHospitals():
    walletaddr=session['walletaddr']
    contract,web3=connect_Blockchain_register(0)
    _users,_passwords,_roles,_names=contract.functions.viewUsers().call()

    contract,web3=connect_Blockchain_drug(walletaddr)
    _lotmanu,_lotid,_lotpillcount,_lotlabform,_lotstatus=contract.functions.viewLots().call()

    contract,web3=connect_Blockchain_drug(walletaddr)
    _waremtransport,_transporters,_warettransport,_transportStatus,_lotidtransport=contract.functions.viewTransport().call()

    data=[]
    for i in range(len(_warettransport)):
        if _warettransport[i]==walletaddr:
            dummy=[]
            lotIndex=_lotid.index(_lotidtransport[i])
            dummy.append(_lotlabform[lotIndex])
            data.append(dummy)
    l=len(data)
    return render_template('distributeHospitals.html',len1=l,dashboard_data1=data)

@app.route('/distributeHospitalsForm',methods=['GET','POST'])
def distributeHospitalsForm():
    drug=request.form['lotlabform']
    hospitalid=request.form['hospitalid']
    count=int(request.form['lotpillcount'])
    print(drug,hospitalid,count)
    contract,web3=connect_Blockchain_drug(session['walletaddr'])
    tx_hash=contract.functions.distributeHospital(session['walletaddr'],hospitalid,drug,count).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return (redirect('/viewDistribution'))

@app.route('/distributeRetailers')
def distributeRetailers():
    walletaddr=session['walletaddr']
    contract,web3=connect_Blockchain_register(0)
    _users,_passwords,_roles,_names=contract.functions.viewUsers().call()

    contract,web3=connect_Blockchain_drug(walletaddr)
    _lotmanu,_lotid,_lotpillcount,_lotlabform,_lotstatus=contract.functions.viewLots().call()

    contract,web3=connect_Blockchain_drug(walletaddr)
    _waremtransport,_transporters,_warettransport,_transportStatus,_lotidtransport=contract.functions.viewTransport().call()

    data=[]
    for i in range(len(_warettransport)):
        if _warettransport[i]==walletaddr:
            dummy=[]
            lotIndex=_lotid.index(_lotidtransport[i])
            dummy.append(_lotlabform[lotIndex])
            data.append(dummy)
    l=len(data)
    return render_template('distributeRetailers.html',len1=l,dashboard_data1=data)

@app.route('/distributeRetailersForm',methods=['POST','GET'])
def distributeRetailersForm():
    drug=request.form['lotlabform']
    retailerid=request.form['retailerid']
    count=int(request.form['lotpillcount'])
    print(drug,retailerid,count)
    contract,web3=connect_Blockchain_drug(session['walletaddr'])
    tx_hash=contract.functions.distributeRetailers(session['walletaddr'],retailerid,drug,count).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return (redirect('/viewDistribution'))

@app.route('/viewDistribution')
def viewDistribution():
    walletaddr=session['walletaddr']
    contract,web3=connect_Blockchain_register(0)
    _users,_passwords,_roles,_names=contract.functions.viewUsers().call()

    contract,web3=connect_Blockchain_drug(walletaddr)
    _retailwaret,_retailers,_retailerlotlabform,_retailercount=contract.functions.viewRetailers().call()
    _hospitalwaret,_hospitals,_hospitallotlabform,_hospitalcount=contract.functions.viewHospitals().call()
    _lotmanu,_lotid,_lotpillcount,_lotlabform,_lotstatus=contract.functions.viewLots().call()
    data=[]
    for i in range(len(_retailwaret)):
        if _retailwaret[i]==walletaddr:
            dummy=[]
            retailerIndex=_users.index(_retailers[i])
            dummy.append(_names[retailerIndex])
            dummy.append(_retailerlotlabform[i])
            dummy.append(_retailercount[i])
            data.append(dummy)
    for i in range(len(_hospitalwaret)):
        if _hospitalwaret[i]==walletaddr:
            dummy=[]
            hospitalIndex=_users.index(_hospitals[i])
            dummy.append(_names[hospitalIndex])
            dummy.append(_hospitallotlabform[i])
            dummy.append(_hospitalcount[i])
            data.append(dummy)
    l=len(data)
    print(data)
    return render_template('viewDistribution.html',len=l,dashboard_data=data)

if(__name__=="__main__"):
    app.run(debug=True)