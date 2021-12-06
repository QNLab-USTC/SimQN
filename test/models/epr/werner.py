from qns.models.epr import WernerStateEntanglement


e1 = WernerStateEntanglement(fidelity=0.95, name="e1")
e2 = WernerStateEntanglement(fidelity=0.95, name="e2")
e3 = e1.swapping(e2)
print(e3.fidelity)

e4 = WernerStateEntanglement(fidelity=0.95, name="e4")
e5 = WernerStateEntanglement(fidelity=0.95, name="e5")
e6 = e4.swapping(e5)
print(e6.fidelity)

e7 = e3.distillation(e6)
print(e7.fidelity)
