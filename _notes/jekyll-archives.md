---
layout: post
date: 2024-02-03
inline: false
related_posts: false
title: jekyll archives is annoying
author: Andrew Boyer
giscus_comments: true
---

`jekyll-archives` is annoying. While I think it does a lot of great things, it is missing a key functionality that would make it awesome. 

Right now, the way `jekyll-archives` works is you can add the following archive categories to your `_config.yml`. Here is what the [documentation](https://github.com/jekyll/jekyll-archives/blob/master/docs/configuration.md) suggests:

```yml
jekyll-archives:
    enabled: []
    layout: archive
    permalinks:
        year: '/:year/'
        month: '/:year/:month/'
        day: '/:year/:month/:day/'
        tag: '/tag/:name/'
        category: '/category/:name/'
```

My own configuration is very similar, following the docs percisely:
```yml
jekyll-archives:
  enabled: [year, tags, categories]
  layouts:
    year: archive-year
    tag: archive-tag
    category: archive-category
  permalinks:
    year: "/blog/:year/"
    tag: "/blog/tag/:name/"
    category: "/blog/category/:name/"
```

Pretty simple right? Wrong.

I thought it would be a good idea to add a custom category, `authors`. While its just me writing on the blog, I wanted to be able to support other authors writing on the blog, and then being able to filter posts by author.

In my head, I thought the following would easily add an `authors` category <d-footnote>I made sure to make the respective `archive-author.liquid` file in `_layouts`.</d-footnote>
:

```yml
jekyll-archives:
  enabled: [year, tags, categories, authors]
  layouts:
    year: archive-year
    tag: archive-tag
    category: archive-category
    author: archive-author
  permalinks:
    year: "/blog/:year/"
    tag: "/blog/tag/:name/"
    category: "/blog/category/:name/"
    author: "/blog/author/:name/"
```


After adding this to `_conig.yml`, I encountered no errors in running the site, and I began setting up my `blog.md` file to begin solidyfing the authors functionality. However, when I visited the `/blog/author/andrew-boyer` location, it did not exist! And yes, I made sure to include the `andrew-boyer` in the `authors` field in my `.md` file [^1].

{% highlight yml linenos %}
jekyll-archives:
  enabled: [year, tags, categories, authors]
  layouts:
    year: archive-year
    tag: archive-tag
    category: archive-category
    author: archive-author
  permalinks:
    year: "/blog/:year/"
    tag: "/blog/tag/:name/"
    category: "/blog/category/:name/"
    author: "/blog/author/:name/"
{% endhighlight %}

<hr>

[^1]: `my test` is hereski!