import json

skin_types = ["oily", "combination", "dry", "normal"]


def main():
    sorted_stats = {}
    for t in skin_types:
        sorted_stats[t] = []
    with open("stats.txt", "r") as f:
        data = json.load(f)
        for p in data.values():
            full_name = p['brand_name'] + ":" + p['product_name']
            for t in skin_types:
                if p[t]['review_sum'] > 50:
                    sorted_stats[t].append([full_name, p[t]['score_sum']/p[t]['review_sum'], p[t]['review_sum']])
    for t in skin_types:
        sorted_stats[t] = sorted(sorted_stats[t], key=lambda item: item[1], reverse=True)
        print(t, ':', len(sorted_stats[t]))
        print('='*50)
        for x in sorted_stats[t]:
            print(x)
        print('\n')


if __name__ == '__main__':
    main()

