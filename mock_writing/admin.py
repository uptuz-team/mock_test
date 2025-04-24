from django.contrib import admin
from .models import Writing, WritingTaskFirst, WritingTaskSecond


class WritingTaskFirstInline(admin.StackedInline):
    model = WritingTaskFirst
    extra = 1
    fields = ('title', 'pdf', 'text', 'img', 'exam_img', 'create_at', 'update_at')
    readonly_fields = ('create_at', 'update_at')


class WritingTaskSecondInline(admin.StackedInline):
    model = WritingTaskSecond
    extra = 1
    fields = ('title', 'topic', 'create_at', 'update_at')
    readonly_fields = ('create_at', 'update_at')


@admin.register(Writing)
class WritingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'ielts', 'allow_time', 'create_at', 'update_at')
    list_filter = ('ielts', 'create_at', 'update_at')
    search_fields = ('title', 'ielts__title')
    ordering = ('-create_at',)
    inlines = [WritingTaskFirstInline, WritingTaskSecondInline]


@admin.register(WritingTaskFirst)
class WritingTaskFirstAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'writing', 'has_pdf', 'has_img', 'create_at', 'update_at')
    list_filter = ('create_at', 'update_at', 'writing')
    search_fields = ('title', 'text', 'writing__title')
    ordering = ('-create_at',)

    @admin.display(description="PDF?")
    def has_pdf(self, obj):
        return bool(obj.pdf)

    @admin.display(description="Rasm?")
    def has_img(self, obj):
        return bool(obj.img or obj.exam_img)


@admin.register(WritingTaskSecond)
class WritingTaskSecondAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'writing', 'short_topic', 'create_at', 'update_at')
    list_filter = ('create_at', 'update_at', 'writing')
    search_fields = ('title', 'topic', 'writing__title')
    ordering = ('-create_at',)

    @admin.display(description="Mavzu qisqacha")
    def short_topic(self, obj):
        return obj.topic[:50] + '...' if len(obj.topic) > 50 else obj.topic
