from django.db import models
from django.urls import reverse

# Create your models here.
# TODO: Set up mapping from class attributes to schema attributes for raw queries
class Anime(models.Model):

    name = models.CharField(
        max_length=255, primary_key=True, verbose_name='AnimeName')
    release_date = models.CharField(
        max_length=255, verbose_name='ReleaseDate', blank=True, null=True)
    release_year = models.IntegerField()
    episode_count = models.IntegerField(
        verbose_name='NumOfEpisodes', blank=True, null=True)

    studio = models.ManyToManyField(
        'Studio',
        db_table='AnimeMadeBy',
        help_text='Each anime can be made by lots of Studios.')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        '''Returns the url to access a particular instance of the model.'''
        return reverse('anime-detail', args=[str(self.name)])


class Studio(models.Model):
    name = models.CharField(
        max_length=255, primary_key=True, verbose_name='StudioName')

    # TODO: We may need a reference to the studio's website
    #website = models.TextField(verbose_name='StudioWebsite', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('studio', args=[str(self.name)])


class User(models.Model):
    # User should have a id as primary key for convenience, though email can also be a primary key
    email = models.EmailField(verbose_name='Email', primary_key=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    # TODO: User avatar
    # avatar = models.ImageField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)

    likeStudio = models.ManyToManyField(
        Studio, help_text='Users like what studios')
    # likeAnime = models.ManyToManyField(
    #     Anime, help_text='Users like what animes')
    likeTag = models.ManyToManyField('Tag')
    likeEpisode = models.ManyToManyField('Episode')

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user', args=[str(self.id)])


class RateAnime(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
    score = models.FloatField()

    class Meta:
        # Use this to represent two cols together as primary keys
        unique_together = (('user', 'anime'), )


class WatchStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
    status = models.IntegerField()

    class Meta:
        # Use this to represent two cols together as primary keys
        unique_together = (('user', 'anime'), )


class Tag(models.Model):
    name = models.CharField(max_length=255, primary_key=True)

    hasAnime = models.ManyToManyField(
        Anime, db_table='TagHasAnime', help_text='Tag has what animes')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag', args=[str(self.name)])


class Episode(models.Model):
    anime_name = models.ForeignKey(Anime, on_delete=models.CASCADE)
    episode_num = models.IntegerField()
    episode_name = models.CharField(max_length=255, blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (('anime_name', 'episode_num'), )

    def __str__(self):
        return self.anime_name + ': ' + self.episode_num

    # TODO: get_absolute_url


class WatchEpisodeProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    watch_time = models.IntegerField(blank=True, null=True)
    date = models.DateField(auto_now=True, blank=True, null=True)
    status = models.IntegerField(help_text='Same as status in WatchStatus')

    class Meta:
        unique_together = (('user', 'episode'), )

class SetTag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    class Meta:
        unique_together = (('user', 'tag'), )

class LikeAnime(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
    class Meta:
        unique_together = (('user', 'anime'), )