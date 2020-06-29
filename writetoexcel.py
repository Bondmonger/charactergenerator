from xlwt import Workbook

    # Workbook is created
wb = Workbook()
    # add_sheet is used to create sheet.
sheet1 = wb.add_sheet('Test')
# sheet1.write(0, 5, '=AVERAGE(F3:f103)')
# sheet1.write(0, 6, '=AVERAGE(g3:g103)')
# sheet1.write(0, 7, '=AVERAGE(h3:h103)')
# sheet1.write(0, 8, '=AVERAGE(i3:i103)')
# sheet1.write(0, 9, '=AVERAGE(j3:j103)')
# sheet1.write(0, 10, '=AVERAGE(k3:k103)')
sheet1.write(1, 1, 'race')
sheet1.write(1, 2, 'class')
sheet1.write(1, 3, 'level')
sheet1.write(1, 4, 'next')
sheet1.write(1, 5, 'str')
sheet1.write(1, 6, 'int')
sheet1.write(1, 7, 'wis')
sheet1.write(1, 8, 'dex')
sheet1.write(1, 9, 'con')
sheet1.write(1, 10, 'cha')

def level_display(levels):
    if len(levels) == 1:
        lvl = str(levels[0])
    elif len(levels) == 2:
        lvl = str(levels[0])+'/'+str(levels[1])
    else:
        lvl = str(levels[0])+'/'+str(levels[1])+'/'+str(levels[2])
    return lvl

def writetosheet(charstats, numberofchars):
    # [[12, 9, 12, 12, 12, 10, 4], [0, 0, 0, 0, 0, 0, 0], ['Bushi'], 'Bushi', ...
    # 'Hengeyokai: Crab', [6], 55000, [60000, 'Bushi']]
    sheet1.write(numberofchars, 1, charstats[4])
    sheet1.write(numberofchars, 2, charstats[3])
    sheet1.write(numberofchars, 3, level_display(charstats[5]))
    sheet1.write(numberofchars, 4, charstats[7][0])
    # sheet1.write(numberofchars, 4, round(sum(generate_hp(ch_classes, charstats[5]))/len(charstats[5])))
    if len(charstats[0]) == 7:
        sheet1.write(numberofchars, 5, charstats[0][0])
    else:
        sheet1.write(numberofchars, 5, str(charstats[0][0]) + '/' + str(charstats[0][7]))
    sheet1.write(numberofchars, 6, charstats[0][1])
    sheet1.write(numberofchars, 7, charstats[0][2])
    sheet1.write(numberofchars, 8, charstats[0][3])
    sheet1.write(numberofchars, 9, charstats[0][4])
    sheet1.write(numberofchars, 10, charstats[0][5])
    wb.save('test.xls')