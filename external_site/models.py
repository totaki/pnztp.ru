# -*- coding:utf-8 -*-
from django.db import models
from prj.settings import MEDIA_ROOT
from PIL import Image
from os import mkdir as os_mkdir
from os import path as os_path
from os import remove as os_remove
from django.db.models import Max
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

FOLDER_FOR_IMAGE = 'image/'



def get_last_id(name):
        from django.db import connection
	seq_name = 'external_site_' + name.lower() + '_id_seq'
	cursor = connection.cursor()
	cursor.execute('select last_value from ' + seq_name)
	return int(cursor.fetchone()[0])

def create_folder(instance, filename):
        inst_class = instance.__class__
        id_max = inst_class.objects.aggregate(Max('id'))['id__max']
        if id_max:
                id_cur = id_max + 1
        else:
                id_cur = get_last_id(inst_class.__name__) + 1
        name_model = inst_class.__name__.lower()
        path_object = name_model + '/' + str(id_cur)
        path_save = FOLDER_FOR_IMAGE + path_object
        path = MEDIA_ROOT + path_save
        try:
                if not os_path.exists(path):
                        os_mkdir(path)
        except OSError:
                return False
        else:
                path_save = path_save + '/' + filename
                return path_save


def folder_for_save(instance, filename):
        if instance.id:
                path_for_save = FOLDER_FOR_IMAGE + instance.__class__.__name__.lower() + '/' + str(instance.id) + '/' + filename
        else:
                path_for_save = create_folder(instance, filename)
        return path_for_save


def lists_in_list(list_, number):
        number_of_lists = (lambda x, y: int(len(x)/y)+1 if len(x)/y - len(x)/int(y) else int(len(x)/y))(list_, number)
        number_of_lists = range(1, number_of_lists + 1)
        return map(lambda x: list_[(x-1)*int(number):x*int(number)], number_of_lists)


def resize_by_width_image(path):
    try:
        image = Image.open(path)
    except IOError:
        return ("Image not found or with is not iamge",)

    MAX_WIDTH = 1024

    if image.size[0] > MAX_WIDTH:
        height = int((float(MAX_WIDTH)/image.size[0]) * image.size[1])
        resized_image = image.resize((MAX_WIDTH, height), Image.ANTIALIAS)
        try:
                resized_image.save(path)
        except IOError:
            return ("Cannot save resized image",)
        finally:
            resized_image.close()
    return ("ok", image)


def return_tmb_path(path):
    """
    Принимает путь до файла
    Функция получает имя файла.
    Возвращает имя файла + _tmb
    """
    try:
        file_name, file_type = os_path.splitext(path)
        return file_name + '_tmb' + file_type
    except TypeError:
        return False


def make_tmb_image(path, image):
    MAX_WIDTH_TMB = 350
    MAX_HEIGHT_TMB = 350

    tmb_path = return_tmb_path(path)

    if image.size[0] > MAX_WIDTH_TMB:
        height = int((float(MAX_WIDTH_TMB)/image.size[0]) * image.size[1])
        image.thumbnail((MAX_WIDTH_TMB, height), Image.ANTIALIAS)
        if image.size[1] > MAX_HEIGHT_TMB:
            image.crop((0, 0, image.size[0], MAX_HEIGHT_TMB))

    try:
        image.save(tmb_path)
    except IOError:
        return "Can't save tmb image"
    finally:
        image.close()
        return "ok"


def resize_and_maketmb(path):
    """
    Принимает путь до файла
    Для работы необходима библиотека PIL.
    Данная функция принимает путь к изображению и изменяет его размер
    если его ширина больше 1024px. Создает изображение-предпросмотр шириной в 350px если его
    ширина больше 350px и обрезает по высоте до 350px, в той же папке прибавляя
    к имени файла '_tmb'.
    Возвращает только статус выполнения.
    """
    image = resize_by_width_image(path)
    if image[0] != "ok":
        return image[0]
    else:
        tmb = make_tmb_image(path, image[1])
    if tmb != "ok":
        return tmb
    else:
        return "ok"


class CommonInfo(models.Model):
        title = models.CharField(max_length=300, verbose_name="Заголовок")
        sketch = models.CharField(max_length=1000, verbose_name="Описание")
        description = models.TextField(verbose_name="Содержание")
        image = models.ImageField(upload_to=folder_for_save, verbose_name="Главное изображение")

        class Meta():
                abstract = True

        @classmethod
        def get_or_false(cls, **kwargs):
                try:
                    return cls.objects.get(**kwargs)
                except cls.DoesNotExist:
                    return False

        @classmethod
        def get_sidebar_list(cls):
                all_objects = cls.objects.all()
                result = ((i.title, i.id) for i in all_objects)
                return list(result)

        @classmethod
        def get_curent_info(cls, id_):
                try:
                        return cls.objects.get(id=id_)
                except ObjectDoesNotExist:
                        return False


class SixImage(models.Model):
        image_1 = models.ImageField(upload_to=folder_for_save, verbose_name="Изображение №1", blank=True)
        image_2 = models.ImageField(upload_to=folder_for_save, verbose_name="Изображение №2", blank=True)
        image_3 = models.ImageField(upload_to=folder_for_save, verbose_name="Изображение №3", blank=True)
        image_4 = models.ImageField(upload_to=folder_for_save, verbose_name="Изображение №4", blank=True)
        image_5 = models.ImageField(upload_to=folder_for_save, verbose_name="Изображение №5", blank=True)
        image_6 = models.ImageField(upload_to=folder_for_save, verbose_name="Изображение №6", blank=True)

        class Meta():
                abstract = True

        def get_images(self, IMAGES_PER_LIST=3):
                all_images = [[1, self.image_1], [2, self.image_2], [3, self.image_3],
                              [4, self.image_4], [5, self.image_5], [6, self.image_6],
                              ]
                images = filter(lambda x: x if bool(x[1]) else False, all_images)
                images = [images[0:IMAGES_PER_LIST], images[IMAGES_PER_LIST:2 * IMAGES_PER_LIST]]
                return images


class News(CommonInfo, SixImage):
        date = models.DateField(auto_now_add=True, verbose_name="Дата создания")

        class Meta():
                ordering = ["-date"]

        def __unicode__(self):
                return self.title

        @classmethod
        def get_sidebar_list(cls):
                result = range(2012, date.today().year + 1)
                return sorted(result, reverse=True)

        @classmethod
        def get_curent_info(cls, page, ppp, year):
                page = int(page)
                all_objects = cls.objects.filter(date__year=int(year))
                return all_objects[ppp*page - 9:ppp*page]


class Announce(CommonInfo):
        start_date = models.DateField(verbose_name="Дата проведения")
        start_time = models.TimeField(verbose_name="Время проведения")
        last = models.BooleanField(verbose_name="Ближайший", editable=False, default=True)

        class Meta():
                ordering = ["start_date"]

        def __unicode__(self):
                return self.title

        @classmethod
        def get_and_check(cls):
                all_objs = cls.objects.all()
                if all_objs:
                        cur_date = date.today()
                        for i in all_objs:
                                if i.start_date < cur_date:
                                        i.delete()
                        all_objs = cls.objects.all()
                else:
                        all_objs = False
                return all_objs


class Rezidents(CommonInfo, SixImage):
        skills = models.CharField(max_length=300, verbose_name="Направления деятельности", help_text="Перечислите через запитую основные направления деятельности", blank=True)
        mail = models.EmailField(verbose_name="E-mail", blank=True)
        site = models.URLField(verbose_name="Страница в интернете", blank=True)
        tele = models.CharField(max_length=300, verbose_name="Телефоны", blank=True)

        def __unicode__(self):
                return self.title


class Infrastructure(CommonInfo, SixImage):
        device = models.CharField(max_length=500, verbose_name="Оборудование", help_text="Перечислите через запитую используемое оборудование")

        def __unicode__(self):
                return self.title


@receiver(post_save)
def postsave_rework_image(instance, **kwargs):
    bases = instance.__class__.__bases__
    if CommonInfo in bases:
        resize_and_maketmb(instance.image.path)
    if SixImage in bases:
        for i in instance.get_images(6)[0]:
            resize_and_maketmb(i[1].path)


class GalleryImage(models.Model):
        image = models.ImageField(upload_to=FOLDER_FOR_IMAGE + 'gallery', verbose_name="Фото")
        comment = models.CharField(max_length=300, verbose_name="Комментарий", blank=True)

        def __unicode__(self):
                return self.comment

        @classmethod
        def get_curent_info(cls, page, ppp, len_list):
                page = int(page)
                all_objects = cls.objects.all()
                for i in all_objects:
                        i.file_name = os_path.basename(i.image.name)
                return lists_in_list(all_objects[ppp*page - ppp:ppp*page], len_list)


@receiver(post_save, sender=GalleryImage)
def save_gallery(instance, **kwargs):
        image_cur = Image.open(instance.image.path)
        if image_cur.size[0] > 1024:
                height = int((1024.0/image_cur.size[0]) * image_cur.size[1])
                resized_image = image_cur.resize((1024, height), Image.ANTIALIAS)
                try:
                        resized_image.save(instance.image.path)
                except IOError:
                        pass
                finally:
                        resized_image.close()
        if image_cur.size[0] > 350:
                height = int((350.0/image_cur.size[0]) * image_cur.size[1])
                image_cur.thumbnail((350, height), Image.ANTIALIAS)
                if image_cur.size[0] > 350:
                        image_cur = image_cur.crop((0, 0, 350, image_cur.size[1]))
                if image_cur.size[1] > 350:
                        image_cur.crop((0, 0, image_cur.size[0], 350))
        list_path = instance.image.path.split('/')
        filename = list_path.pop()
        list_path.extend(['thumbs', filename])
        list_path = '/'.join(list_path)
        try:
                image_cur.save(list_path)
        except IOError:
                pass
        finally:
                image_cur.close()


@receiver(pre_delete, sender=GalleryImage)
def delete_gallery(instance, **kwargs):
        file_for_delete = instance.image.path
        os_remove(file_for_delete)


class GovermentOrg(CommonInfo):
        ORGANIZATIONS = (('TP', 'Технопарк Яблочков'),
                         ('GKU', 'ГКУ ПРОБИ'),
                         ('INNO', 'УИПиСП Пензенской области')
                         )
        org = models.CharField(max_length=4, choices=ORGANIZATIONS, unique=True)

        def __unicode__(self):
                return self.org


class Utility(models.Model):
        name = models.CharField(max_length=15, unique=True)
        bool = models.BooleanField(blank=True)
        char = models.CharField(max_length=15, blank=True)
