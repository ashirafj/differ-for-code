a, b, c = map ( int , input ( ) . split ( ) )

for i in range ( a , b ) :
    if i % c == 0 :
        ans += 1

print ( ans )
print ( )
