class Document:

    def __init__(self, document_id, title, dataset_id, pages) -> None:
        self.document_id = document_id
        self.title = title
        self.dataset_id = dataset_id
        self.pages = pages