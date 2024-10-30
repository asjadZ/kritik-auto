class ProviderData:
    def __init__(self, title = None, excerpt = None, content = None, image = None):
        self.title = title
        self.excerpt = excerpt
        self.content = content
        self.image = image

    def get_title(self):
        return self.title
        pass

    def get_excerpt(self):
        return self.excerpt
        pass

    def get_image(self):
        return self.image
        pass

    def get_content(self):
        return self.excerpt
        pass

class Provider:

    def __init__(self, url):
        self.data: ProviderData = None
        self.url = url

    def get_data(self):
        return self.data

    def fetch_data(self):
        pass