try:
    from langchain.output_parsers import ResponseSchema
    print("langchain.output_parsers")
except ImportError:
    try:
        from langchain_core.output_parsers import ResponseSchema
        print("langchain_core.output_parsers")
    except ImportError:
        try:
            from langchain_community.output_parsers import ResponseSchema
            print("langchain_community.output_parsers")
        except ImportError:
            print("NotFound")
