import json
CONTRACT = "contracts/contract.py"

def project(contract, vm, alice, bob):
    vm.sender = alice
    pid = contract.create_project(bob, "Analytics dashboard", "Build a responsive analytics dashboard for the client's existing reporting API.", "Deliver dashboard views, filters, CSV export, tests, and deployment documentation.", "Native mobile apps, payment processing, and changes to the reporting API are excluded.")
    vm.sender = bob; contract.accept_project(pid); return pid

def verdict(gate, cost, time, risk):
    return json.dumps({"gate":gate,"impact":{"cost":cost,"time":time,"risk":risk},"rationale":"The proposal was compared directly with the signed baseline.","amendment":"Agree additional budget and delivery time."})

def test_only_bound_contractor_accepts(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=direct_deploy(CONTRACT); direct_vm.sender=direct_alice
    pid=c.create_project(direct_bob,"Portal","Build the agreed customer reporting portal and documented workflows.","Responsive portal, account views, reports, tests, and operator documentation.","Mobile applications and payment processing are expressly excluded.")
    with direct_vm.expect_revert("Only the contractor"): c.accept_project(pid)
    direct_vm.sender=direct_bob; c.accept_project(pid); assert c.get_project(pid)["status"]=="ACTIVE"

def test_in_scope_authorization_is_single_use(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=direct_deploy(CONTRACT); pid=project(c,direct_vm,direct_alice,direct_bob); direct_vm.sender=direct_alice
    direct_vm.mock_llm("SCOPE LOCK",verdict("IN_SCOPE",10,12,8))
    cid=c.request_change(pid,"filters-1","Implement the dashboard date and region filters listed in the deliverables.","This completes an explicit baseline deliverable.")
    direct_vm.clear_mocks(); assert c.is_authorized(cid)
    direct_vm.sender=direct_bob; c.consume_authorization(cid); assert not c.is_authorized(cid)
    with direct_vm.expect_revert("not active"): c.consume_authorization(cid)

def test_change_order_requires_both_signatures(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=direct_deploy(CONTRACT); pid=project(c,direct_vm,direct_alice,direct_bob); direct_vm.sender=direct_bob
    direct_vm.mock_llm("SCOPE LOCK",verdict("CHANGE_ORDER",70,65,45))
    cid=c.request_change(pid,"mobile-1","Add native iOS and Android applications with offline synchronization.","The client requested a new mobile distribution channel.")
    direct_vm.clear_mocks(); assert not c.is_authorized(cid)
    direct_vm.sender=direct_alice; c.approve_change_order(cid); assert not c.is_authorized(cid)
    direct_vm.sender=direct_bob; approved=c.approve_change_order(cid); assert approved["status"]=="AUTHORIZED" and c.is_authorized(cid)

def test_out_of_scope_never_authorizes(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=direct_deploy(CONTRACT); pid=project(c,direct_vm,direct_alice,direct_bob); direct_vm.sender=direct_alice
    direct_vm.mock_llm("SCOPE LOCK",verdict("OUT_OF_SCOPE",90,90,85))
    cid=c.request_change(pid,"pay-1","Replace the client's accounting system and process customer card payments.","This unrelated request was added after project acceptance.")
    direct_vm.clear_mocks(); assert c.get_change(cid)["status"]=="REJECTED" and not c.is_authorized(cid)

def test_replay_wrong_party_and_cancel_fail_closed(direct_vm,direct_deploy,direct_alice,direct_bob,direct_charlie):
    c=direct_deploy(CONTRACT); pid=project(c,direct_vm,direct_alice,direct_bob); direct_vm.sender=direct_charlie
    with direct_vm.expect_revert("Only a project party"): c.request_change(pid,"x-1","Attempt unrelated work from an unbound wallet.","No authority exists for this request.")
    direct_vm.sender=direct_alice; direct_vm.mock_llm("SCOPE LOCK",verdict("IN_SCOPE",5,5,5))
    cid=c.request_change(pid,"same-1","Add automated tests required by the signed deliverables.","The baseline explicitly requires tests.")
    direct_vm.clear_mocks()
    with direct_vm.expect_revert("already been used"): c.request_change(pid,"same-1","Try to replay a previous request identifier.","Replay must fail before consensus.")
    c.cancel_project(pid); assert not c.is_authorized(cid)
