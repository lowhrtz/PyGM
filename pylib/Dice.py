import random
import re


random.seed()
DIVIDER = 'd'

def randomInt( lower, upper ):
    return random.randint( lower, upper )

def rollString( dice_string ):
    single_dice_format = re.compile( '^[d]{0,1}[0-9]+$' )
    dice_format = re.compile( '^[0-9]+[d][0-9]+$' )
    complex_format = re.compile( '^\\(?[0-9]+[d][0-9]+(\\s*\\+[0-9]+\\s*)?\\)?(\\s*[x|×]\\s*[0-9]+)?$' )

    if single_dice_format.match( dice_string ):
        sides = int( dice_string.replace( 'd', '' ) )
        return randomInt( 1, sides )

    elif dice_format.match( dice_string ):
        dice_string_list = dice_string.split( DIVIDER )
        number = int( dice_string_list[0] )
        sides = int( dice_string_list[1] )
        result = 0
        for _ in range( number ):
            result += randomInt( 1, sides )
        return result 

    elif complex_format.match( dice_string ):
        dice_string_list = dice_string.split( DIVIDER )
        number = dice_string_list[0].replace( '(', '' )
        after_div = dice_string_list[1].replace( '(', '' )
        sides = ''
        add = ''
        sub = ''
        mul = ''
        div = ''

        for i in range( len( after_div ) ):
            if after_div[i].isdigit():
                sides += after_div[i]
            else:
                break
        if '+' in after_div:
            plus_split = after_div.split( '+' )
            after_plus = plus_split[1]
            add = ''
            for i in range( len( after_plus ) ):
                if after_plus[i].isdigit():
                    add += after_plus[i]
                else:
                    break
        if 'x' in after_div or '×' in after_div:
            if 'x' in after_div:
                x_split = after_div.split( 'x' )
            else:
                x_split = after_div.split( '×' )
            after_x = x_split[1]
            for i in range( len( after_x ) ):
                if after_x[i].isdigit():
                    mul += after_x[1]
                else:
                    break
        sides = int( sides )
        base_roll = 0
        for _ in range( sides ):
            base_roll += randomInt( 1, sides )
        total = base_roll
        if add:
            total += int( add )
        if mul:
            total *= int( mul )
        return total
    return -1
