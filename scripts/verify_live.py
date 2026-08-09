import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import patch_status
patch_status.apply()
from genlayer_py import create_account, create_client
from genlayer_py.chains import testnet_bradbury
from genlayer_py.abi import calldata
from genlayer_py.abi.transactions import serialize
from genlayer_py.contracts.utils import make_calldata_object
import eth_utils

TERMINAL={"ACCEPTED","FINALIZED","UNDETERMINED","CANCELED"}
def env_value(path,name):
    for line in open(path,encoding="utf-8"):
        if line.strip().startswith(name+"="): return line.split("=",1)[1].strip().strip('"').strip("'")
    raise RuntimeError(name+" not found")
def account(key): return create_account(account_private_key=key if key.startswith("0x") else "0x"+key)
def client(acct): return create_client(chain=testnet_bradbury,account=acct)
def wait(c,tx,label):
    for i in range(120):
        rec=c.get_transaction(transaction_hash=tx); status=str(rec.get("status_name") or rec.get("status")); print(label,i,status,flush=True)
        if status in TERMINAL:
            if status not in {"ACCEPTED","FINALIZED"}: raise RuntimeError(label+" "+status)
            return
        time.sleep(8)
    raise TimeoutError(label)
def read(c,acct,address,fn,args=None):
    data=[calldata.encode(make_calldata_object(method=fn,args=args or [],kwargs=None)),b"\x00"]
    res=c.provider.make_request(method="gen_call",params=[{"type":"read","to":address,"from":acct.address,"data":serialize(data),"transaction_hash_variant":"latest-nonfinal"}])["result"]
    raw=res["data"] if isinstance(res,dict) else res
    return calldata.decode(eth_utils.hexadecimal.decode_hex("0x"+raw))
def write(c,address,fn,args):
    tx=c.write_contract(address=address,function_name=fn,args=args,value=0); print(fn,tx,flush=True); wait(c,tx,fn); return str(tx)
def main():
    root=os.path.dirname(os.path.dirname(__file__)); desktop=os.path.dirname(os.path.dirname(root))
    primary=account(env_value(os.path.join(os.path.dirname(root),".env"),"GENLAYER_PRIVATE_KEY"))
    contractor=account(env_value(os.path.join(desktop,"sansh genlayer","accounts.env"),"ACCOUNT_1_GENLAYER_PRIVATE_KEY"))
    pc,cc=client(primary),client(contractor); address=json.load(open(os.path.join(root,"deployment.json")))["address"]; txs=[]
    txs.append(write(pc,address,"create_project",[contractor.address,"Analytics dashboard","Build a responsive analytics dashboard for the client's existing reporting API.","Deliver dashboard views, date and region filters, CSV export, tests, and deployment documentation.","Native mobile apps, payment processing, and reporting API changes are excluded."]))
    stats=read(pc,primary,address,"get_stats"); pid="scope-"+str(stats["projects"])
    txs.append(write(cc,address,"accept_project",[pid]))
    txs.append(write(pc,address,"request_change",[pid,"live-change-1","Add native iOS and Android applications with offline synchronization.","The client requested an additional mobile distribution channel after signing the dashboard scope."]))
    stats=read(pc,primary,address,"get_stats"); cid="change-"+str(stats["changes"]); change=read(pc,primary,address,"get_change",[cid])
    if change["gate"]!="CHANGE_ORDER": raise RuntimeError("Expected CHANGE_ORDER, got "+change["gate"])
    txs.append(write(pc,address,"approve_change_order",[cid])); txs.append(write(cc,address,"approve_change_order",[cid]))
    if not read(pc,primary,address,"is_authorized",[cid]): raise RuntimeError("Bilateral authorization missing")
    txs.append(write(cc,address,"consume_authorization",[cid])); final=read(pc,primary,address,"get_change",[cid]); print(json.dumps(final,indent=2,default=str))
    if final["status"]!="CONSUMED": raise RuntimeError("Authorization was not consumed")
    with open(os.path.join(root,"verification.json"),"w",encoding="utf-8") as f: json.dump({"project":pid,"change":cid,"transactions":txs,"gate":final["gate"],"status":final["status"]},f,indent=2)
if __name__=="__main__": main()
