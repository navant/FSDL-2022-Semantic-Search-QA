from jina import Client, DocumentArray

if __name__ == "__main__":
    c = Client(host="grpcs://0.0.0.0")
    da = c.post("/qa", DocumentArray.empty(2))
    print(da.tensors)
