import collections
import itertools
import numpy as np
import os
import uuid

from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import ModelFormWithFileField
from .models import Item, Comparison, Tag, TaggedItem

def index(request):

    return render(request, 'index.html')

def compare(request):
    if request.method == 'POST':
        if request.POST['chosen'] == '1':
            item_1_uuid = uuid.UUID(request.POST['item_1_uuid'])
            item_2_uuid = uuid.UUID(request.POST['item_2_uuid'])
            comp = Comparison.objects.create(item_better = Item.objects.get(uuid = item_1_uuid), item_worse = Item.objects.get(uuid = item_2_uuid))
            comp.save()
        elif request.POST['chosen'] == '2':
            item_1_uuid = uuid.UUID(request.POST['item_1_uuid'])
            item_2_uuid = uuid.UUID(request.POST['item_2_uuid'])
            comp = Comparison.objects.create(item_better = Item.objects.get(uuid = item_2_uuid), item_worse = Item.objects.get(uuid = item_1_uuid))
            comp.save()

    item_1 = Item.objects.random()
    item_2 = Item.objects.random()

    while item_1 == item_2:
        item_2 = Item.objects.random()

    return render(request, 'compare.html', { 'item_1': item_1, 'item_2': item_2 })

def upload_file(request):
    if request.method == 'POST':
        form = ModelFormWithFileField(request.POST, request.FILES)
        items = Item.objects.all()

        for i in range(Item.objects.count()):
            if os.path.exists("./uploads/" + request.FILES['file'].name):
                form = ModelFormWithFileField()
                return render(request, 'upload.html', { 'form': form })

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = ModelFormWithFileField()

    return render(request, 'upload.html', { 'form': form })

def list_items(request):
    items = list(Item.objects.filter().order_by('place'))

    return render(request, 'list.html', { 'items': items })

def files(request):
    items = list(Item.objects.all())

    return render(request, 'files.html', { 'files' : items })

def tag(request):
    tags = list(Tag.objects.all())

    if request.method == 'POST' and 'tag' in request.POST:
        items = list(Item.objects.all())
        for _item in items:
            if _item.uuid.__str__() in request.POST:
                _tag = Tag.objects.get(uuid=uuid.UUID(request.POST['tag']))
                taggedItems = TaggedItem.objects.filter(item=_item, tag=_tag)
                if len(taggedItems) == 0:
                    taggedItem = TaggedItem(item=_item, tag=_tag)
                    taggedItem.save()
    elif 't' in request.GET:
        items = list(Item.objects.all())
        _tag = Tag.objects.get(name=request.GET['t'])
        return render(request, 'tag.html', { 'tags': tags, 't': _tag, 'items': items })

    return render(request, 'tag.html', { 'tags': tags })

def search_tags(request):
    tags = list(Tag.objects.all())

    if request.method =='GET' and 't' in request.GET:
        _tag = Tag.objects.get(name=request.GET['t'])
        taggeditems = list(TaggedItem.objects.filter(tag=_tag))
        return render(request, 'search_tags.html', { 'tags': tags, 'taggeditems': taggeditems })

    return render(request, 'search_tags.html', { 'tags': tags })

def calculate_ranks(request):
    items = Item.objects.all()
    count = Item.objects.count()

    if count == 0:
        return render(request, 'calculate_ranks.html', { 'no_items': True })

    comparisons = np.zeros((count, count))

    for i in range(count):
        for j in range(count):
            better_count = Comparison.objects.filter(item_better=items[i], item_worse=items[j]).count()
            worse_count = Comparison.objects.filter(item_better=items[j], item_worse=items[i]).count()
            if better_count + worse_count == 0:
                comparisons[i][j] = 0.5 # Make then equal if there are no comparisons
            else :
                comparisons[i][j] = better_count / (better_count + worse_count) # Ratio of better comparisons to total comparisons

    pref_values = calculate_ble(comparisons)

    ranking = np.argsort(pref_values)

    for i in range(count):
        item = items[int(ranking[i])]
        item.place = i
        item.save()

    return render(request, 'calculate_ranks.html', { 'no_items': False })

def calculate_ble(comparisons, max_iter=100):
    length = comparisons.shape[0]

    wins = np.sum(comparisons, axis=0)

    params = np.ones(length, dtype=float)

    for _ in range(max_iter):
        tiled = np.tile(params, (length, 1))
        combined = 1.0 / (tiled + tiled.T)
        np.fill_diagonal(combined, 0)
        nxt = wins / np.sum(combined, axis=0)
        nxt = nxt / np.mean(nxt)
        if np.linalg.norm(nxt - params, ord=np.inf) < 1e-6:
            return nxt
        params = nxt
    raise RuntimeError('did not converge')