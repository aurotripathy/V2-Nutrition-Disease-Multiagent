# https://openfoodfacts.github.io/openfoodfacts-python/usage/

# also try https://go-upc.com/plans/api for code-to-name lookup

from openfoodfacts import API, APIVersion, Country, Environment, Flavor
import pprint   
import time
import argparse
from collections import defaultdict
import logging


def get_nutriments_from_open_food_facts(food_item: str) -> dict:
    """
        Fetches the nutriments (ingredients or nutrients) for a given food item from Open Food Facts
        using the Open Food Facts API.

        Args:
            food_item: A string representing the food item to search for.

        Returns:
            A dictionary of nutriments for the food item, or an empty dictionary if no nutriments are found.
        """
    print(f"[🔧C] Toolcall: Getting nutriments for {food_item} from Open Food Facts ---")

    api = API(
        user_agent="MyAwesomeApp/1.0",
        username="off",
        password="off",
        country=Country.us,
        flavor=Flavor.off,
        version=APIVersion.v2,
        environment=Environment.net, #staging server, not production
        timeout=10, # looks to be the minimum timeout
    )

    logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"Searching Open Food Facts for {food_item}")
    print(f"[🔧C] Toolcall: Searching Open Food Facts for {food_item}") # cant see this in the logs
    start_time = time.time()
    nutriments = {}
    try:
        
        result = api.product.text_search(food_item)  # returns a dict
        # if not result:
        #     logging.debug(f"No result found for {food_item}")
        #     return {}
        # logging.debug(f"Result: {result}")
        
        # Look in the "result" object for the 'products' list, then print the 'nutriments' for each product if present
        products = result.get('products', [])
        # logging.debug(f"Products in the result for: {products}")

        if products:
            nutriments = products[0].get('nutriments')
            logging.debug(f"\n***** Nutriments *****: {nutriments}")

            if nutriments is None:
                logging.debug(f"No nutriments found for the product: {food_item}")
            else:
                logging.debug(f"Nutriments found for the product: {food_item}")
        else:
            logging.debug(f"No products found in the search result for: {food_item}")

    except Exception as e:
        logging.debug(f"Error searching products: {e}")
    finally:
        elapsed = time.time() - start_time
        logging.debug(f"API call took {elapsed:.2f} seconds")
    
    return nutriments


def group_nutriments(nutriments_dict: dict) -> dict:
    """
    Groups nutriments dictionary entries into a nested dictionary structure.
    
    Args:
        nutriments_dict: A dictionary of nutriments from Open Food Facts API.
    
    Returns:
        A nested dictionary where:
        - First level keys are the base nutrient names (before first delimiter)
        - Second level contains only entries with "_value", "_unit", and optionally "_serving"
    """
    # Step 1: Group entries by base name (before first "_")
    # Base name may contain '-' but should be extracted before the first '_'
    
    groups = defaultdict(dict)
    for key, value in nutriments_dict.items():
        if '_' in key:
            # Split by '_' first - base name is everything before first '_'
            # This allows base names like "saturated-fat" to be preserved
            base_name = key.split('_')[0]
        else:
            # No delimiters, use key as base name
            base_name = key

        groups[base_name][key] = value
    
    
    logging.debug(f"Grouped nutriments (by base name): {dict(groups)}")

    # Step 2 & 3: Filter each group to retain only _value, _unit, and _serving entries
    grouped_result = {}
    
    for base_name, group_items in groups.items():
        filtered_group = {}
        
        # Retain items containing "_value" and strip the base name prefix
        for key, value in group_items.items():
            if '_value' in key:
                # Remove the base_name prefix to get just "value"
                simplified_key = key.replace(f"{base_name}_", "")
                filtered_group[simplified_key] = value
        
        # Retain items containing "_unit" and strip the base name prefix
        for key, value in group_items.items():
            if '_unit' in key:
                # Remove the base_name prefix to get just "unit"
                simplified_key = key.replace(f"{base_name}_", "")
                filtered_group[simplified_key] = value
        
        # Retain items ending with "_serving" and strip the base name prefix
        for key, value in group_items.items():
            if key.endswith('_serving'):
                # Remove the base_name prefix to get just "serving"
                simplified_key = key.replace(f"{base_name}_", "")
                filtered_group[simplified_key] = value
        
        # Only add the group if it has at least one filtered entry
        if filtered_group:
            grouped_result[base_name] = filtered_group
    
    return grouped_result

def get_grouped_nutriments_from_open_food_facts(food_item: str) -> dict:
    """
        For the given food item, fetches the nutriments from Open Food Facts
        using the text-search Open Food Facts API. 
        Arranges the nutriments into groups by the base name (before the first underscore) and returns a dictionary of these groups.

        Args:
            food_item: A string representing the food item to search for.

        Returns:
            A dictionary of nutriments for the food item, or an empty dictionary if no nutriments are found.
        """

    nutriments = get_nutriments_from_open_food_facts(food_item)
    return group_nutriments(nutriments)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get nutriments from Open Food Facts')
    parser.add_argument('search_term', type=str, help='Search term for the food product')
    args = parser.parse_args()
    
    search_term = args.search_term
    
    print(f"{30*'-'} Search term: {search_term} {30*'-'}")
    print(f"Getting nutriments for {search_term} from Open Food Facts and grouping them:")   
    print(f"{60*'-'}")

    grouped_nutriments = get_grouped_nutriments_from_open_food_facts(search_term)
    for nutrient_name, nutrient_data in grouped_nutriments.items():
        print(f"{nutrient_name}: {nutrient_data}\n")

    # Legacy code: getting nutriments from Open Food Facts flat (un-grouped), one line per nutrient
    # print(f"{30*'-'} Search term: {search_term} {30*'-'}")
    # print(f"Getting nutriments for {search_term} from Open Food Facts flat (un-grouped), one line per nutrient:")   
    # print(f"{60*'-'}")
    # nutriments = get_nutriments_from_open_food_facts(search_term)
    # for nutrient_name, nutrient_data in nutriments.items():
    #     print(f"{nutrient_name}: {nutrient_data}")