from impl import BasicQueryEngine, CategoryQueryHandler, CategoryUploadHandler


def main() -> None:
    db_path = "relational_basic_demo.db"
    data_path = "data/scimago.json"

    uploader = CategoryUploadHandler()
    uploader.setDbPathOrUrl(db_path)
    uploader.pushDataToDb(data_path)

    category_handler = CategoryQueryHandler()
    category_handler.setDbPathOrUrl(db_path)

    engine = BasicQueryEngine()
    engine.addCategoryHandler(category_handler)

    categories = engine.getAllCategories()
    areas = engine.getAllAreas()

    print(f"Total categories: {len(categories)}")
    print(f"Total areas: {len(areas)}")

    if categories:
        first_category = categories[0]
        print("First category IDs:", first_category.getIds())
        print("First category quartile:", first_category.getQuartile())

        first_id = first_category.getIds()[0] if first_category.getIds() else None
        if first_id:
            entity = engine.getEntityById(first_id)
            print("Entity by ID:", entity.__class__.__name__, entity.getIds())
    else:
        print("No categories loaded.")


if __name__ == "__main__":
    main()
