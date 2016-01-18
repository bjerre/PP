from django.shortcuts import render, get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from dicer.models import Category
from dicer.models import Page
from django.http import HttpResponse
from dicer.forms import CategoryForm
from dicer.forms import PageForm
from dicer.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from dicer.bing_search import run_query
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from dicer.models import Post
from django.utils import timezone
from dicer.forms import PostForm




def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits


    response = render(request,'dicer/index.html', context_dict)

    return response
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    #context_dict = {'boldmessage': "I am bold font from the context"}
    #context = RequestContext(request)
    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    #category_list = Category.objects.order_by('-likes')[:5]
    #page_list = Page.objects.order_by('-views')[:5]
    #context_dict = {'categories': category_list, 'pages': page_list}

    #for category in category_list:
        #category.url = category.name.replace(' ', '_')

    #page_list = Page.objects.order_by('-views')[:5]
    #context_dict['pages'] = page_list

    #return render(request, 'dicer/index.html', context_dict)

#def index(request):
#    return HttpResponse("Dicer says: hey there world! <br/> <a href='/dicer/about'>About</a>")


def about(request):
    context_dict = {'boldmessage': "I am also bold from the context"}
    return render(request, 'dicer/about.html', context_dict)

#def about(request):
#    return HttpResponse("Dicer says: here is the about page! <br/> <a href='/dicer/'>Index</a>")

def category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    if not context_dict['query']:
        context_dict['query'] = category.name

    return render(request, 'dicer/category.html', context_dict)

def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'dicer/add_category.html', {'form': form})


def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
                cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # probably better to use a redirect here.
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form':form, 'category': cat}

    return render(request, 'dicer/add_page.html', context_dict)

def add_post(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
                cat = None

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            if cat:
                post = form.save(commit=False)
                post.category = cat
                post.save()
                # probably better to use a redirect here.
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PostForm()

    context_dict = {'form':form, 'category': cat, 'category_name_slug': category_name_slug}

    return render(request, 'dicer/add_post.html', context_dict)

@login_required
def restricted(request):
    return render(request,'dicer/restricted.html')


def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'dicer/search.html', {'result_list': result_list})

def get_category_list(max_results=0, starts_with=''):
        cats = []
        if starts_with:
                cats = Category.objects.filter(name__istartswith=starts_with)

        if max_results > 0:
                if cats.count() > max_results:
                        cats = cats[:max_results]

        return cats

def suggest_category(request):

        cats = []
        starts_with = ''
        if request.method == 'GET':
                starts_with = request.GET['suggestion']

        cats = get_category_list(8, starts_with)

        return render(request, 'dicer/cats.html', {'cats': cats})

def track_url(request):
    page_id = None
    url = '/dicer/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

@login_required
def like_category(request):

    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes =  likes
            cat.save()

    return HttpResponse(likes)


@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)

            pages = Page.objects.filter(category=category).order_by('-views')

            # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages

    return render(request, 'dicer/page.html', context_dict)

#def post_list(request):
    #posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    #return render(request, 'dicer/post_list.html', {'posts': posts})

#def post_detail(request, pk):
#    post = get_object_or_404(Post, pk=pk)
#    return render(request, 'dicer/post_detail.html', {'post': post})

#def post_new(request, category_name_slug):

    #try:
        #cat = Category.objects.get(slug=category_name_slug)
    #except Category.DoesNotExist:
               # cat = None

#    if request.method == "POST":
 #       form = PostForm(request.POST)
  #      if form.is_valid():
  #          if cat:
  #              post = form.save(commit=False)
  #              post.category = cat
  #              post.author = request.user
  #              post.published_date = timezone.now()
  #              post.save()
  #          return category(request, category_name_slug)
  #      else:
  #          print form.errors
  #  else:
   #     form = PostForm()
   # return render(request, 'dicer/post_edit.html', {'form': form, 'category': cat, 'category_name_slug': category_name_slug})

#def post_edit(request, pk):
#    post = get_object_or_404(Post, pk=pk)
#    if request.method == "POST":
#        form = PostForm(request.POST, instance=post)
#        if form.is_valid():
##            post = form.save(commit=False)
#            post.author = request.user
#            post.published_date = timezone.now()
#            post.save()
##            return redirect('post_detail', pk=post.pk)
 #   else:
 #       form = PostForm(instance=post)
 #   return render(request, 'dicer/post_edit.html', {'form': form})