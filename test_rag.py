from rag.vector_store import add_research, find_similar_research, debug_closest_match, MAX_DISTANCE



def check(label, topic):
    print(f"\n--- {label} ---")
    print(f"Query: {topic!r}")

    debug = debug_closest_match(topic)
    print(f"Closest match: '{debug['closest_topic']}' "
          f"(raw distance: {debug['distance']})")

    result = find_similar_research(topic)
    if result:
        print(f"=> CACHE HIT (distance {result['distance']} <= threshold {MAX_DISTANCE})")
    else:
        print(f"=> CACHE MISS (distance {debug['distance']} is above threshold {MAX_DISTANCE}, "
              f"or store is empty)")

def main():
    print("=" * 60)
    print("SmartRoute-MCP — Vector Cache Test")
    print(f"(current similarity threshold: {MAX_DISTANCE})")
    print("=" * 60)

    print("\nAdding research notes for: 'why the ocean is salty'")
    add_research(
        "why the ocean is salty",
        "- Rain erodes minerals from rock on land.\n"
        "- Rivers carry these dissolved minerals to the sea.\n"
        "- Evaporation removes pure water, leaving salts behind.",
    )
    check("Test 1: similarly-worded topic (expect a close distance)", "why is the sea salty")
    check("Test 2: unrelated topic (expect a much larger distance)", "best programming languages for beginners")

    print("\n" + "=" * 60)
    
    #print("\n--- Test 1: similarly-worded topic (should be a CACHE HIT) ---")
    #result = find_similar_research("why is the sea salty")
    #if result:
    #    print(f"HIT - matched '{result['matched_topic']}' "
    #          f"(distance: {result['distance']})")
    #    print(f"Reused notes:\n{result['notes']}")
    #else:
    #    print("MISS - no similar research found "
    #          "(if this surprises you, try lowering max_distance in "
    #          "find_similar_research, or check that the embedding model "
    #          "downloaded correctly the first time you ran this)")

    #print("\n--- Test 2: unrelated topic (should be a CACHE MISS) ---")
    #result2 = find_similar_research("best programming languages for beginners")
    #if result2:
    #    print(f"Unexpected HIT - matched '{result2['matched_topic']}' "
    #          f"(distance: {result2['distance']}) - consider lowering "
    #          f"max_distance if unrelated topics keep matching")
    #else:
    #    print("MISS - correctly found nothing relevant")

    #print("=" * 60)


if __name__ == "__main__":
    main()
