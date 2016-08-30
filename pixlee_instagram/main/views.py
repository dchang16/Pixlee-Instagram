from datetime import datetime
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import Context, Template
from django.shortcuts import redirect, render
from django.core import serializers

from .forms import SearchForm, NameForm
from .models import Item

import dateutil.parser
import logging
import requests


logger = logging.getLogger(__name__)

# Renders index page
def index(request):
	if request.session.get("name", None) != None:
		return show_collection(request)
	name_form = NameForm()
	return render(request, "main/index.html", {"name_form": name_form})

# Renders search page
def search(request):
	search_form = SearchForm()
	return render(request, "main/search.html", {"search": search_form})

# Renders result page
def result(request, objects):
	return render(request, "main/result.html", objects)

# Renders collection page
def show_collection(request):
	item_list = Item.objects.filter(name=request.session["name"])
	paginator = Paginator(item_list, 8)

	page = request.GET.get('page')
	try:
		items = paginator.page(page)
	except PageNotAnInteger:
		items = paginator.page(1)
	except EmptyPage:
		items = paginator.page(paginator.num_pages)

	return render(request, "main/collection.html", {"items": items})

# Renders error page
def error_page(request):
	return render(request, "main/error.html")

# Creates form for user inputted name
def enter_name(request):
	if request.method == "POST":
		form = NameForm(request.POST)
		if form.is_valid():
			request.session["name"] = form.cleaned_data["name"]
		else:
			return error_page(request)

	return show_collection(request)

# Helper for serializing instagram HTTP response into list of objects
def serialize_response(response, start_date, end_date):
	items = []
	for obj in response["data"]:
		object_map = {}
		try:
			created_time = datetime.fromtimestamp(int(obj["created_time"]))
			created_date = created_time.date()
			commented_time = datetime.fromtimestamp(int(obj["caption"]["created_time"]))
			commented_date = commented_time.date()
			if (created_date >= start_date and created_date <= end_date) or \
				(commented_date >= start_date and commented_date <= end_date):
				object_map["type"] = obj["type"]
				object_map["user"] = obj["user"]["username"]
				object_map["link"] = obj["link"]
				object_map["url"] = obj["images"]["standard_resolution"]["url"] if obj["type"] == "image" \
									else obj["videos"]["standard_resolution"]["url"]
				object_map["tagtime"] = unicode(created_time) \
				if created_time > commented_time else unicode(commented_time)
				items.append(object_map)
			else:
				continue
		except:
			pass
	return items

# Handles validation, parsing, and creating HTTP response. Stores a session for client sided caching
def search_tags(request):
	request.session["items"] = []
	request.session["page"] = []
	request.session["total"] = 0
	items = []
	tag = ""
	if request.method == "POST":
		form = SearchForm(request.POST)
		if form.is_valid():
			tag = form.cleaned_data["tag_field"]
			start_date = form.cleaned_data["start_date"]
			end_date = form.cleaned_data["end_date"]
			URL = "https://api.instagram.com/v1/tags/{}/media/recent?access_token={}"\
				.format(tag, settings.INSTAGRAM_KEY)
			response = requests.get(URL).json()
			items = serialize_response(response, start_date, end_date)
		else:
			return error_page(request)
	else:
		return error_page(request)
	request.session["tag"] = tag
	request.session["start_date"] = unicode(start_date)
	request.session["end_date"] = unicode(end_date)
	request.session["items"].append(items)
	request.session["current_page"] = 0
	request.session["page"].append((1, response))
	request.session["total"] = 1
	return result(request, {"items": request.session["items"][0], "tag": tag, "page": 0})

# Handles pagination for next result
def next_tag(request):
	page_index = request.session.get("current_page", None)
	current_page = page_index + 1
	request.session["current_page"] = current_page
	if current_page >= request.session.get("total"):
		previous_response = request.session["page"][page_index][1]
		next_URL = previous_response["pagination"]["next_url"].replace("\u0026", "&")
		response = requests.get(next_URL).json()
		FMT = '%Y-%m-%d'
		items = serialize_response(response, datetime.strptime(request.session["start_date"], FMT).date(),\
		datetime.strptime(request.session["end_date"], FMT).date())
		request.session["page"].append((current_page, response))
		request.session["total"] += 1
		request.session["items"].append(items)
		return result(request, {"items": request.session["items"][current_page],\
		"tag": request.session["tag"], "page": current_page})
	else:
		return render_page(request, page_index + 1)

# Obtains previous result
def prev_tag(request):
	request.session["current_page"] -= 1
	return render_page(request, request.session["current_page"])

# Helper for rendering results from search given a page number
def render_page(request, page_number):
	return result(request, {"items": request.session["items"][page_number],\
	"tag": request.session["tag"], "page": page_number})
	
# Saves collection to database
def save_to_collection(request):
	for items in request.session["items"]:
		for elem in items:
			item = Item(type=elem["type"], user=elem["user"],link=elem["link"], \
				url=elem["url"], name=request.session["name"],\
				tagtime=datetime.strptime(elem["tagtime"], '%Y-%m-%d %H:%M:%S'))
			try:
				item.save()
			except:
				pass 
	return show_collection(request)

# Logs user out, and deletes session
def delete_session(request):
	request.session.flush()
	return index(request)


