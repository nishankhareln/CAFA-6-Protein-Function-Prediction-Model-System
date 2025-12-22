from scripts.ontologyparser import GOGraphParser

GO_OBO = r"D:\CAFA project\data\go-basic.obo"
OUTPUT = r"D:\CAFA project\go_parser.pkl"

parser = GOGraphParser(GO_OBO)

with open(OUTPUT, "wb") as f:
    import pickle
    pickle.dump(parser, f)

print("GO parser saved correctly")
