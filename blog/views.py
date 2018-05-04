from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.shortcuts import redirect
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator
from watson_developer_cloud import PersonalityInsightsV3


# Create your views here.

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    tone_analyzer = ToneAnalyzerV3(
        username='63dc8916-f3af-49ae-aaa9-21a0afb94efc',
        password='kKio6x7rYMb4',
        version='2016-05-19 ')

    language_translator = LanguageTranslator(
        username='f91625cc-500e-4489-9a3c-2dd83888f064',
        password='TzSE4wZqtgBT')

    personality_insights = PersonalityInsightsV3(
        version='2017-10-13',
        username='7e7d3458-4318-4c05-b55b-c8a84ee37f25',
        password='puPMIxm6kxiU'
    )

    # print(json.dumps(translation, indent=2, ensure_ascii=False))

    for post in posts:
        posting = post.text
        toneObj = json.dumps(tone_analyzer.tone(tone_input=posting,
                                                content_type="text/plain"), indent=2)
        post.toneObj2 = json.loads(toneObj)
        post.angerScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][0]['score']
        post.disgustScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][1]['score']
        post.fearScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][2]['score']
        post.joyScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][3]['score']
        post.sadScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][4]['score']

        translation = language_translator.translate(
            text=post.text,
            source='en',
            target='es')
        obj = json.dumps(translation, indent=2, ensure_ascii=False)
        post.obj2 = json.loads(obj)
        post.translate_spanish = post.obj2['translations'][0]['translation']
        post.count = post.obj2['word_count']
        post.charactercount = post.obj2['character_count']


        translation1 = language_translator.translate(text=post.text,source='en',target='ar')
        kobj = json.dumps(translation1,indent=2,ensure_ascii=False)
        post.kobj=json.loads(kobj)
        post.translate_korean = post.kobj['translations'][0]['translation']

        profile = personality_insights.profile(content=post.text, content_type="text/plain",raw_scores=True,
                                               consumption_preferences=True)
        personobj = json.dumps(profile, indent=2, ensure_ascii=False)
        post.obj3 = json.loads(personobj)

        # The raw score for the characteristic.
        post.score0 = post.obj3['personality'][0]['raw_score']
        post.score1 = post.obj3['personality'][1]['raw_score']
        post.score2 = post.obj3['personality'][2]['raw_score']
        post.needs = post.obj3['needs'][0]['raw_score']
        # The normalized percentile score for the characteristic
        post.percentile0 = post.obj3['personality'][0]['percentile']
        post.percentile1 = post.obj3['personality'][1]['percentile']
        post.percentile2 = post.obj3['personality'][2]['percentile']
        # ndicates whether the characteristic is meaningful for the input language. The field is always true for all characteristics of English, Spanish, and Japanese input.
        post.significance0 = post.obj3['personality'][0]['significant']
       # post.significance1= post.obj3['personality'][1]['significant']

        # Big 5 characteristics of personality insights and their percentiles
        post.openness = post.obj3['personality'][0]['children'][0]['percentile']
        post.conscientiousness = post.obj3['personality'][0]['children'][1]['percentile']
        post.extraversion = post.obj3['personality'][0]['children'][2]['percentile']
        post.Agreeableness = post.obj3['personality'][0]['children'][3]['percentile']
        post.Emotional_range = post.obj3['personality'][0]['children'][4]['percentile']

        #post.openness = post.obj3['personality'][0]['child']
       # = post.obj3['tree']['children'][0]['children'][0]['children'][1]['percentage']

    return render(request, 'blog/post_list.html', {'posts': posts})
#def post_detail(request,pk):
#    Post.objects.get(pk=pk)
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})