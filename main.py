from crawler.sherdog_parser import parse_fighter_page


if __name__ == "__main__":

    parse_queue = ["/fighter/Rafael-dos-Anjos-11675"]
    parsed = set()

    while len(parse_queue) != 0:
        print("queue: {}, parsed: {}".format(len(parse_queue), len(parsed)))
        ref = parse_queue.pop()
        if ref in parsed:
            continue
        parsed.add(ref)
        fighter, fight_infos = parse_fighter_page(ref)
        parse_queue += [fi.fighter2_ref for fi in fight_infos]
