import requests as r
import pandas as pd
from sys import argv

def flat_iterable(iter: dict | list, prefix: str = '', key_delimiter: str ='', return_dict = {}) -> dict:
    itype = type(iter)
    assert itype is dict or itype is list
    if itype is dict:
        for k, v in iter.items():
            if type(v) is dict or type(v) is list:
                flat_iterable(v, f'{prefix}{key_delimiter}{str(k)}', '.', return_dict)
            else:
                return_dict[f'{prefix}{key_delimiter}{str(k)}'] = v
    elif itype is list:
        for i, v in enumerate(iter):
            if type(v) is dict or type(v) is list:
                flat_iterable(v, f'{prefix}{key_delimiter}{str(i)}', '.', return_dict)
            else:
                return_dict[f'{prefix}{key_delimiter}{str(i)}'] = v
    return return_dict

def get_game_result(game: int = 0) -> r.Response:
    assert game >= 0
    api = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/"
    url = api + str(game) if game > 0 else api
    return r.get(url)

def get_games_results(min_game: int = 1, max_game: int = 1, step: int = 1) -> list:
    assert min_game >= 1 and max_game >= 1 and step >= 1 and max_game >= min_game
    results = []
    for i in range(min_game, max_game + 1, step):
        print(f'INFO: getting result for the game {i}')
        for _ in range(10):
            game_result = get_game_result(i)
            if game_result.ok:
                results.append(flat_iterable(game_result.json()).copy())
                break
        else:
            print(f"\033[31mFAIL: it was not possible reach game {i}\033[m")
    return results

def get_latest_game_number():
    return get_game_result().json()['numero'] 

def print_invalid_command():
    print('ERROR: invalid command format')
    print('usage: python3 lotofacil.py -min [int32] -max [int32] -o [output.csv]')

def main():
    if len(argv) != 7 or not '-min' in argv or not '-max' in argv or not '-o' in argv:
        print_invalid_command()
        exit(1)
    args = {argv[i]: argv[i + 1] for i in range(1, len(argv), 2)}
    try:
        args['-min'] = int(args['-min'])
        args['-max'] = int(args['-max'])
        args['-o'] = args['-o'] + '.csv' if not args['-o'].endswith('.csv') else args['-o']
        assert args['-max'] <= get_latest_game_number(), f'`-max` greater than {get_latest_game_number()} which is the latest game number'
        assert args['-max'] >= args['-min'], f'`-min` is greater than `-max`'
        assert args['-min'] >= 1, f'`-min` must be greater or equal than 1'
    except AssertionError as e:
        print(f'ERROR: {e}')
        exit(1)
    except Exception as e:
        print(f'ERROR: {e}')
        print_invalid_command()
        exit(1)
    
    results = get_games_results(args['-min'], args['-max'])
    pd.DataFrame(results).set_index('numero').to_csv(
        path_or_buf=args['-o'],
        decimal=',',
        sep=';',
        encoding='iso-8859-1'
    )
    

if __name__ == '__main__':
    main()