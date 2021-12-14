from django.shortcuts import render
import numpy as np
from django.http import HttpResponse
from django import forms
from django.conf import settings
from AdversarialTool.sentiment_analysis import predictSentiment , predictStress, predictEmotions
from AdversarialTool.attackFineTunedModel import getAttackOutput
from AdversarialTool.attackEmotionsModel import getEmotionAttackOutput
from django.utils.safestring import mark_safe
from django.forms import Textarea


ATTACK_CHOICES= [
    ("Choose an attack: ","Choose an attack: " ),
    ('BERT-ATTACK', 'BERT-ATTACK(Default)'),
    ('PWWS','PWWS'),
    ('Genetic', 'Genetic'),
    ('SememePSO', 'SememePSO'),
    ('FD', 'FD'),
    ]

class NewForm(forms.Form):
    inputText = forms.CharField(widget=forms.Textarea, label='')
    chosenAttack= forms.CharField(label=mark_safe('<br />'), widget=forms.Select(choices=ATTACK_CHOICES))
    widgets = {
        'text': Textarea(attrs={'spellcheck': 'true', 'rows': 5})
        }


def index(request):
    
    if request.method == "POST":
        givenText = request.POST.get("inputText")
        attackType= request.POST.get("chosenAttack")

        textInputted=True
        classifier=predictStress(givenText)
        if classifier['label']=='LABEL_1':
            label=1
            classifier="Stressed"
        elif classifier['label']=='LABEL_0':
            classifier="Not Stressed"
            label=0

        attackOutput=getAttackOutput(givenText,label, attackType)

        attackOutputClasification=AttackClassification(attackOutput, label)
        attackSucess=isAttackSucessful(attackOutput)
        if attackSucess:
            attackOutputResults=attackOutput["result"]
        else:
            attackOutputResults=givenText

        return render(request, "AdversarialTool/index.html", {
        "form":NewForm(request.POST), "textInputted":textInputted, "givenText":attackOutputResults, "startingClassification":classifier,
        "attackedClassification":attackOutputClasification, "attackSucess":attackSucess
    })
    else:
        return render(request, "AdversarialTool/index.html", {
            "form":NewForm(), "textInputted":False, "givenText":""
        })

def emotions(request):
    if request.method == "POST":
        givenText = request.POST.get("inputText")
        attackType= request.POST.get("chosenAttack")

        textInputted=True
        classifier=predictEmotions(givenText)

        attackOutput=getEmotionAttackOutput(givenText,attackType)
        print(attackOutput)
        attackSucess=isAttackSucessful(attackOutput)
        if attackSucess:
            attackOutputResults=attackOutput["result"]
        else:
            attackOutputResults=givenText

        attackOutputClasification=predictEmotions(attackOutputResults)[0]
        return render(request, "AdversarialTool/emotions.html", {
        "form":NewForm(request.POST), "givenText":givenText, "startingClassification":classifier[0], "textInputted":textInputted, "attackSucess":attackSucess
        ,"OutputResults":attackOutputResults, "attackedClassification":attackOutputClasification
    })
    else:
        return render(request, "AdversarialTool/emotions.html", {
            "form":NewForm(), "textInputted":False, "givenText":""
        })
def FAQ(request):
    return render(request, "AdversarialTool/FAQ.html")

def examples(request):
    return render(request, "AdversarialTool/examples.html")

def about(request):
    return render(request, "AdversarialTool/about.html")

def aboutAttacks(request):
    return render(request, "AdversarialTool/aboutAttacks.html")



def AttackClassification(attackDict, label):
    if attackDict["success"] and label==1:
        return "Not Stressed"
    elif attackDict["success"] and label==0:
        return "Stressed"
    elif not attackDict["success"] and label==1:
        return "Stressed"
    else:
        return "Not Stressed"
def isAttackSucessful(attackDict):
    if attackDict["success"]:
        return True
    else: 
        return False
