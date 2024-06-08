---
layout: page
title: Shows
permalink: /favs/shows/
description: All posts in the "shows" category.
---

<h1>Shows</h1>
<ul>
  {% for post in site.favs %}
    {% if post.categories contains 'shows' %}
      <li>
        <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
        <p>{{ post.excerpt }}</p>
      </li>
    {% endif %}
  {% endfor %}
</ul>
