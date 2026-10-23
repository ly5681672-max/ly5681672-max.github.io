# frozen_string_literal: true

# Assign numeric note sequence before jekyll-paginate-v2 sorts the posts.
# Source Markdown and dates remain unchanged.
Jekyll::Hooks.register :site, :post_read do |site|
  site.posts.docs.each do |post|
    title = post.data["title"].to_s
    numbers = title.scan(/(?:\A|[-_\s])0*(\d{1,3})(?=[-_\s]|\z)/).flatten

    if numbers.length == 1
      post.data["note_order"] = numbers.first.to_i
    else
      post.data["note_order"] = -1
      Jekyll.logger.warn("note_order:", "#{post.relative_path} 无法唯一识别编号")
    end
  end
end
