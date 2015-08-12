from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dixy.views.home', name='home'),
    # url(r'^dixy/', include('dixy.foo.urls')),

    url(r'^dixy/$', 'dixy_viz.views.home', name='home'),
    url(r'^dixy$', 'dixy_viz.views.home', name='home'),
    url(r'^dixy/test/$', 'dixy_viz.views.test', name='test'),
    url(r'^dixy/viz/(-{0,1}\d*)$', 'dixy_viz.views.d3_viz', name='d3 visualization'),
    url(r'^dixy/network/(.*)$', 'dixy_viz.views.network', name='network visualization'),
    url(r'^dixy/about/$', 'dixy_viz.views.about', name='about'),
    url(r'^dixy/contact/$', 'dixy_viz.views.contact', name='contact'),
    url(r'^dixy-private/$', 'dixy_viz.views.home', name='home'),
    url(r'^dixy-private/test/$', 'dixy_viz.views.test', name='test'),
    url(r'^dixy-private/viz/(-{0,1}\d*)$', 'dixy_viz.views.d3_viz', name='d3 visualization'),
    url(r'^dixy-private/network/(.*)$', 'dixy_viz.views.network', name='network visualization'),
    url(r'^dixy-private/about/$', 'dixy_viz.views.about', name='about'),
    url(r'^dixy-private/contact/$', 'dixy_viz.views.contact', name='contact'),
    url(r'^dixy-pol/$', 'dixy_viz.views.home', name='home'),
    url(r'^dixy-pol/test/$', 'dixy_viz.views.test', name='test'),
    url(r'^dixy-pol/viz/(-{0,1}\d*)$', 'dixy_viz.views.d3_viz', name='d3 visualization'),
    url(r'^dixy-pol/network/(.*)$', 'dixy_viz.views.network', name='network visualization'),
    url(r'^dixy-pol/about/$', 'dixy_viz.views.about', name='about'),
    url(r'^dixy-pol/contact/$', 'dixy_viz.views.contact', name='contact'),


    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
