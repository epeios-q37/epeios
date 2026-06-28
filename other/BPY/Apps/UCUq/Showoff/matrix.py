import base64
import random
import zlib

import ucuq

ANIMATION_ = (
    "eJztVct2xCAI/SU0jsaliv7/J1UeEtNm2q66KieTnHiBe0Hi4BA7xrNlfZ5v8NdI+2vvn/C6gKfFaVGfXh7I97Il1PxVorAIqdnSjZqOedyFJ2WuQxLd1E4DXcnmP399x+OOp8/xJytPi/JLG4E7l6gk0t/xi4gggdKTyn2IBvZVbFM68sYgRTVOFJWHXTi++j2/WzgxFHLK564AhnaPbrkJq3YYk+DWEGCZReI75wwLQ6usyg4ny2848poO0yWir40CgrJuClojePcpvrFa0JjR27gbMOQX3ZZ/w6Nb1IH261CXY/Mm/XMMsAo5QzZ1K3OyNdZn5VQlRJv0eBN0SOnYR06G4zW1Mv55Lm3lleurWER1dCevjS7TH2wO14f2Iq99KtL2QG6YvzayiYSeR6X6PKeLt40k33rQpeRTLmzxVPoEXTYd54WDtKDHNfW6sszzhOBsiqtCB9uYMUjCW7X893iQz7WGcWrP3e3MECG5wKjRXmHsNtlCgAFuLGZ3w6d3TKDj9hA/31JQPD/EzxLKPAuC9u/JbLvyM26HaPkB98+4S9/jfh358Iyf8Ev8zV9LeFPXv/2lfQDZZCB0",
    "eJzlVG2WhSAI3ZJZav6MhP0vaRTQ0KYzCxjeO8fi48IFDGgVNx1hNiIb4mNHgiU+ynHKUepvlo1Y5bodrftLuj6M/LOkj7gu8Kpvlp08n1Ghir506QmVxaGgQ7J6KB3YXvjQ8dtDPA2YxAkzqUJforVvmofrSxxvSB8cWZqqaTEt9XX8INqyTqN32AnVFB6WVYHDvgl+OLSYQY9u9lT+6TL5kf/JZCE4BawoZhmTlZjdUadD8sT8cmft/dwe4BKGL2HrVvEylMx21+2ttLvlh1sUDw32bDGueaexm1wV8lNku3emP2Td8ImXlHYzmbWf8cE4vdYabVP4NTxXJE4bpG2mddHB6Pb2dJlGNH2qd1Obl5pmsJKisKQBydP3ho2uGSh/HCRVkeWIMOoDGlcjrx2UisagQDAxUPID0QzykIFhJCjifk79Odi3oCcfqO9gfuKlIWm7CLT/bvrQObluBSQ/Mv422RvdEsjv1HcMJ3tFy4enuEvxbrnTrcSrFnEeA27uSNVtt5N1CSaptedq99/xWINd68n9e7yrd+109NqbLic8vr/a9Ra9l1fVfR73h71fkA981/XrJ3W1/xX/Vf+H/n/JD0YcHxU=",
    "eJy9VFmW7SAI3JJJHD+d2P+SniggSSfdf49zh4SCArG0wbY4vg0CfJkZ34BRZfv6Awew68WvPxUKB6ZzBgEVbq9lsjQh+9FNZcDc67dHF1/5hYGTe1qZF7ybo4UkXU6REtttDm9WPvyO6lvdbtz4QZnM3x/FHOFJ5yuzhMQnQBYn4iETfV+kYoYm4yR+FPEbP+cgO49zWksax/yi9mdEZ91BpjrTLlzApYOnJbBrmXV24xfdYrV6fZ30NKO7QuySSJqtHRIU9g7OQQX8aYeubZgOW8tx1VdGwW2WM5Uj2TsnI+3YD1lKsTnfU4LCypOBGMMtQSnprgYcjcFuqpHi8HhS+ei8qfYh4TA67wXejtiaVduHuSGn5Jd9nEnWFQUkg2406yaciS6WZW7XyuI5tsQKbaqDVIC38eIjxDtS/D51FR/liLP8+l4LMkp/50y8Rn8eMTvrWxBV1DlrlzvkBHxnJRDVr0ZKKBD7Kmfxo/lH/61HksvMV9M/ZsESDGQ8dlqjHD18dizeR/HkG34gv4OQgTbngaOuWoRwSLs/SpzGL7lUms8TPw3J9T3/wrvBfPOHaBb/HRGLfOX4d5zXvvf9bpf7Hd9n4h0/ze+4Yf8Hv/kr/3z3/1/7B0Q6HlU=",
    "eJyFVVmWhCAMvBKgiHyCwP2PNGQl2D0zvH6oWSqVkNB9rFVxL/RxijTh3lV0kzjSoxkrj29u0yeDT+8XfQR6HMbCYXAOnDeY8SiyWwLDurNG0dj/MvFJ7yXwtsSvC/650XyhrEf70Aci49+4L3/GL1zvysnU3XjiVwveX2AzzCcDu85vQgMpZZTjrBT0zVa6glSmqAcbd9sCZt1MNlDUtEAEv7Id6hrUuxp9JLHySLoJfkH9wxQjk1n4DR0e9nLjvS7JE0rVsF5clI66YuuQI/FrKw3Yq0wFuWaK1YcwSuMk4wdkya/uNYygYxtZfzsBXGcgynyCYK0nDB19wFaz2gdOCyhCIhfWR8/f0OA0IZp3QL2MbUXkhPqglKodbxxB4Hd5PYE6tDXwPSAb8jc5VmCviRT0yXPL91gjqBNLgPVoJJILSk89aZvkNKScdRsFHjOhH8BK/W9uisbjyJeJrVoAbVRqXeqLyxPXxDVp+Fm32cBYkepHecV10BF9yyRc/eBaTEaqP7Ap2hQdgcidYO4MOPCvffiuiPfK36GgTz020IUZSwNT/pDrvAuwfkWnY1VrmjzXrP9DeTq9b5nf/OVS9Yz3qXPoc9UwIsQ5pWi7SZtx7nNIk+4QU37NNvJumAHe/cN0xnZ13/Fznv5+/HJFmvb85YLtMjyffxG4HumH47veS8U+ryQS+7/1xf2td+c/epT/AGzGHSA=",
    "eJy1VVuSxCAIvJImGvTTF/c/0o6IiGa29mupqVixhW5AMsmgWKRnxs1eOFvd8XoC7e1v6ZnwG0030A4O+TTI8fB22azq+G3StINuqMB7LEWETqQMIbK9/Dt/7CwVpRig+C2dq6gtq9XQ8TITY3844phB+T3ZXGZ9zJbmSpdZdN0VDgTUhcOh9zTPa9FxVNKOM7w1zSrph2a8bCzK/+K1jhLBpUkpbmUewhu5PlrfVr8cD/5pR52Uvh6McsgzjQoat6SO9edy+EeuTGT9dDotPHAykakvPG3sGC5Teokc8c3Q5Eip1W0I6onp7f9wHmPxuwiQeRgtalb5N3I2RPhBaSqAk2HzAweR0xYlb7n50qHm9vhsaR423bWas01+4razZTt3QY8fjVjHkxvtAsH9HERL/K/Zsn1Pdhtf14KwMi3bF4vrr2QmVF2fZxV+rVtdZVxqE/66puLhWhYZm7wF8/OeiiQ3GNim6CqU1GZpROKmV4lJ5+SL8UjAyDmF7iH4xR0GtHJ5Pi/CHziuQSNf8c9P/LNcijkpduuJ4fwetF7yuxdeOH5E9TFUf06WawHobsGX0v7mR/4h6U1ldmxd5hfcvPDwDQ9r1204x3d//aX9u/0AGOgf/g==",
    "eJyFVVmWxCAIvJLRGONnu93/SBNkT8+88SOvtSgoEOy19grw6UtX4E1XfO6fZX8TwXUojggdNDKIit/W/9ePtQ6Dr8vjEPs08XlN9L+a4N3qFv5HmFMJO4/50vTxfGI1OWpO7DBaEM+OXyQRZmYXfxhVGP9Ek8xhkvAfZaVRlqs6N4bfUHLVvNkuWMbh3JgVMCmqW6T6aLpRzEyaLPcJfTpc1bPOjvoO5l1Wx/Uyf7wVCxQXbEFPDRunTLWyuqUO78X3R1Ub7YVzd1Rvbvw39g8mNb+sbsJJf3wnGEhZwouZNibiTgcaR4tfrP/XFfbUTbiVIdJcFmmzn3ndXeMThKNsdaRdZ22awVNH9Z+gZkiS7SN8GqOJn6kyZOp3VxRMdoh7TbZx6qrxnsiXkwAFuvT+EyrfByAkbLWnuCTLDDHBUQDr07xJJjSkGMCoEO4me5d4nVut8DlQAROIFQFqJ19nmpq6e/5ebVx0EBGkPmn6CnQtlM4irwGbbPgVT2eRk0tvtdNYP7Nq2+4yfI46BC86YlPGjfObthj8AjzkSPwoH1oHsqq+YrdWNYqWfkt+zf2lJAx4ZcG74pVKdK/PFIYZoCCC+aa/cMolBc+Q3fafpBOCe4DohX3wu9rDtfwuYDviOv/Bf+HHv3Eag3D/ADg4HfQ=",
    "eJyFVFsSwyAIvBJJjcbP+uD+R2pQQNF2ynQa4rosDw1GRAR8YzOHeEQgLyHbu+GB3Pw4z+8k/8TJAA96VLzJb3yfGTtm/FT+W7iv9n91fChDZbxqFGMusNN1WszS3A6AY7wv3kaTcClwKiRM+hj5AXOZI6DghTO7NMmJsLy6Ob42uCqeZsJlsxo4C/a+YcZheebfuFlZ9FZ9aGq+L13C0UQp/1RIhQJ5GzWqMjf+lOyLiV+JH5SG0sikwcDwZZvKER5GmcA7eF85B2D4o1joYrfZpl1Odr/WX3F6jJE81RiFENCaZ77MqUzByA7mc7n3ygc5aJxeWfTlmHiWyAv+YmWJsk5f6pe7serf9tRW2pfGMJ78D9EfNgXp80k6jlVfKudx3ISX+aK2Cn07e4+TCY9mSHrqaRX8XIziSeIf15DUDNmSqFm+uc+xQe4rPlI3RepFpEZEpyKbUdeOdgfPFVINoGgRVpw/z4yn7WtZ5Q+I6jZ+Ff6IZiybQna8fl9Wa619yZvb8GDw3Yqh/eAH82bMaxLf8TYQ+I1ng2/t6/F1OW74afD9DtgDscePf3D/B4efbx83xiGs",
    "eJylVNuygyAM/CWUmz6KmP//pGNCEkCwPTPdaSmw2WS5FQDAGLju9v4cAFsM2D8i0BScOAUbdpK7J3xekPA3BQcQTIBIwe4OMxGTQAbWA6W1OMjLrQooNThR+A00PODEUlQOGIa+VymHHhPxu/Ab8YcGmzsD9i7mVwrGFlLhUQFW+KhVGIlaz6N8Vj5DbU1s5YWXlDSxcjb3zM8JuUDkOM9WNQsvMJk6zG3FBx9Vz7je9D0S/2bleefXPmLIv0knqP5s1ldOoYdrha76FhgqtlTDNRvFOapjS7HU+09Fn6OsUi9IhacwWwbXyJfpRc30FQi5XuppmuI/QbM/PTLy8rbG/AN2Xo994eVM2Ud+nrH4S324ojkm5PzLtiDQ9ZUeWaRrecetRDKOypN010bq753PZ31+rrpLNDpbvty/wOMAPQznN8XVGdtk4gzqcRDlWt63fHADfwiP0p2sdXdvFR636rCDSU2Gha5RrwO0btdqSVfYWI+0P9uUp2LkdvZHwE9o1CvQujFDyl5P1PrKLx/0bjrb63/h564q5q4q3p7gf/lf63/jJ/+43+v/AZsrIHQ=",
    "eJzlVFuSxCAIvBLRJJrP+OD+R1oQVMxkdw6wVGUMNi0NMsGCGDdsFnIgJ4hT6XH0RMQCmBBPLOVEPJACPHlMoOeiJbGTESFzGLEaQfADMVV2CbsL43c7i3EveaDwcRsGT8EXnwYtPS2Nv5/Y9jCSczN1QxdEWwsDwdNGhcCDz4tjleQ4ggq/7wLxDwsdLucIm6GKRmi/lBo0aKSWQCd7h8HR4ru0ozlQTu2WmPTeTYKEukO8o4xTNEg3vF5TnXh4pMUpVPV94slkFsur22cD21WjNGTIQFuthEoU33ILMzgsxG5pvImUc9nuaBhMFbx3fPKj5WtYNZmizX9YzXPcA2fKEz+MXtHvRVR5xWn4rof+MLJCW9fxsPVLnSBinmFD574KX/uZWhVp8oPiZZSpgOvHpEWFnSG2q9/3SzIx+MTPueGt06+jWtzbctZmND11cZ8BHV2mJk48qqT+dxnfJbVNG9HHqT74oCdDl8uWLV5tfv/sn+vzYPUtJR1Wn7ffLTQn61b2D/2dqZJL4y8p3af+2+K7dSIYMWiZqj/PKt7w2rqdf8dvI/bFYHyX3237goP7G3df+P/OfgB8AR78",
    "eJzFVFuyrCAM3FJAFP1EIftf0iUvCWrd+TypKQbopNMJmUFE3CqeiH1ZK+LRL3BFtuX+6nhD8sGNwI0uEKPgqfKKZ+BjZwhCswteVj3UihIIT/5Onvt1JrzvL6w4LGVmwVYOYo/kfhkNSWIectq6W73uxFHwZaW1f65EMSf7CSWrhUaenWxn/kb7opWQNxRe++eimEK1VlcGRIlB2En6QvtgeE8FB6+9LQu1JoxAlZ2sk0CaGUwqkYUoXRYaGD1BeRawdsGNWzgzg3RdNPRsnFLtupVMPYcDcSAmeFjUEdFWu/gmF0pWXbw8t0gB038LsW0cdXU7NPN5xz8sDPciERPcnHJfn3XEm+R3s/NwE34tfH/HH87L3Hysrx8zvgxQx98OLv+JNu5RYuef0B3C40vJdACCSxRtbUOf9WQ8A0iyNJdxetx9qVrruvwO6sAt+xhXmBJmfUDFc8HZLO7Cb8vzq77a2lRZ85fne1tu/9ke/anTpTvouGTmc48SVZHqP/MDB+2wUk4HweWg45aY3xUZcOpYra/45Cm3j7FXP0nDrzE5RY9DcmJUkscXljY9FqhOcebStzeuFupI+YXv1//j1184d2semckZnNgPC/Ln+yN++4G//k3/zv4BUSseAA==",
    "eJyNVFmWxCAIvBJtFvWzXbj/kYbNiObNm2F6kmhRUIAJIlnBhvxj6/SHX3ws0v9NHvxjSBw7HgMjS6hBsBamtgdqwjUaryPvxbmhdlQMRMbSNcyDB+Xnhid5DYUHB7lGYvKHiJkzlq+outlF8n8UL4ULkhQmLWsGYjFyiWagsDevhV+iYlJosbSl8R6lvrCniYdqhVyd05ycuA/99NAPuVL5F+8BC7k55qVqILEnYDsp4MlEwB7lJnyQTlLCcLOWW3A0nCjp5ChJGkE3ftAJgmqXrvCC8yfuCmgrwHoAolQ3QuNdlTEGae4iHXTczwS74FlPQOVnGK197JRTQKECT0dC14mNSdpe0W07W3YUYeJ6/TSX3/ApeG509Qu4GYwj7pCPXC1wsZuLrFKvLdDMmj1xNEiDSgOij/+rmaCngfNdiU6FDXXmw+WtdQOc+arH686WUnLkfA1dR6PH41PQ1gbDiZ2W4fs3XSUbuByQPcq8FYsw3euCjzZYHe03vnWh9Q3va1e2LxPPTetPa/bHguHjuPhk6n8v+vfpH0axvD27YPqoizHb6hc4j6/p05fX8cEGNShl44Pps612OTGKL6f6iC88eLzv/bMv1dq36BfV/DRM8kWJnR6f37XHmsfD+nERyR7P+cX/+MU3vviLc75elHPBRfrShFWsrJb6F4P0oqx4+AOH/+BO8g8L8x32",
    "eJyNVFu2wyAI3JLxEZPP+GD/S7qCYDCN7eWctuowwwhpAAAiQAAoALZtKi4qUBRQsat1vZctJwF4WseJQML4SWPzHploJ1BmBDf0r37UBY5moeW4Txt5eCkzdPK6IguveL7WPyOay+K/Ym7ku1HlhKsdkiMvEVPI0tZxl7A5DTSiaDv/uq9B978saiYkFmU8BazZTkITDPEmcsv20oul2nCLXwUiGuCRuNxtxxqw9IW5pIBTaUfHheY2iO5ETTyBgHzTS5kDPbWNsdQMXNNA+T4HtQNxbE20yLeCtyOT8SZt4+mHGpEq482j8Tg85LfSvqahv/FsjUwVczCX2wAznhDPkaiHtPqge26DfyZyneUR3WkcXukbNTpZGCk1JiibfONxFFSjTrdKUAdGDKp0rwSt+BtCc/0RCndvON+sjquwCvev+Dt1evpHA9Lgn7pKFZky5KrWz1MZikOfXHJaHriZ8JE2kDIBQfE3jct/54MvD23/2Ve4vBvgmceNsaL/eKcJ34i/59T8JCMzu3s/83fOeJ098dKDP0fmRtQFbhgPC5zfdOAX+LZ0BsyLX/XF1wr3S+c9xP/rs6/wlX+r/6CvEb7ypxfEa8QfePmBr24msXYGP5T/g/8Bz2ge6g==",
    "eJyFVFuShCAMvBIgiH6KkPsfac0T0KE25RaQTjqdwA4AuHpBBfzYCi8xyNnBBg3wGyyDcxKJa0UPfiCBG7hDUo6eajXgwnzlKpqWxZNsRykFXtY0TBcmrnVI6mGlIkNWf0NCk5RRYN+z3Z0/U0IlEZHO1Yh3prSyTLCbTNEHp8r+oa9Q/YybHJTEP/PrfaeGu+uZdDKNxOCY42wYHrmRjFUT58sNOtK0sZ425G989kk8KWBOxFok+RL55HsCL49MAQvlYUze485BdhF9m/Un/fNLenJ9RN+NxBRxsNvR8Tm4HesH5KJRSX9x5+DqNpyl5ycpeKYl0TOk/FpwfzfBcSmMV7dLVw52rR8ortqkArduV5qAX7jijlntzTj6o6lG6oHxUwkOqhi48IFnwpPeYzUWsaaayTLP8O54mRPiIj/KMZiK/rwf89egX+wc+DU4D/gBg0l/OXbX59/0xV/GxDaVoafGyP7JM80WCXMzE35OYjUsG+U15ZzD3o0e7e/DL574xcMo/KW/mmsfg+13qPPEsdjwYzKr1EXChtkfE94++Jyv00jw21Z+tR/XMJnWrwtc+Vc8iocF/o57m17DscD9K26Vf/+DXwtc+Vf9q/3X30qf2qo/te87YvsDs2AefA==",
    "eJylVEm2hCAMvBKDTEsRuP+RPpkwavtc/PQgJFSlEsAxRp8fslbxnybHPhIObBrK2qg0qOIJgiCYDKxnfLqt57k3PJenRJhtE79rCcB3/OFG0fhd5fDw24S/jlXhYm/DOBxQJC7aDitUxRXZItHW04nKSE3Db5Xa+0oikhq7s4wjMQRmqyJE62f8Mi+y/ConrmAnsr58TUWOjb21cWi/LJr5G4pzwtkoVeF4ZDFzIyi1pYBd/Wu4DUdnTCJqt5RXmKQoreX8LNkHWDLx1kIoAPHSD+tR//SEAuNduiX45uB/LvRzA8KBzpS4nRFPsgfgMImhZcTE+iu6E+Y3kzDUDmPYKjxZHd0ZJh3mpmKtUeIR4xsWazaQuUNg0/iOySd+auvQTUP6DWs0cuCmINud6jANnOwqaKTzvvoTx7oBnNpI29YeG+pZITxSFyHwQqxuGKSVs5HPuL7mRm4UPbdxM9HfKJJPTVSK4SPe8om5vGfE1B1w2i9n/3x7UJLzBfTAU7z8yqKQXBjr6yreNGHRPu0Kj7xixOUucc2fNZ7r0j0hV3wCL/jymp/wXBjvWH2sypf8byzyCI8412cfgZ/8+W0Z2/tufaRhix/x9hH/0eaLvbaJ7dmfq33V/8X/3/gfJh4fkg==",
    "eJzlVVuWrCAM3FJAFPwUIftf0iQhgTjtnL7/l2N3GyqVykNsRCwdaQH6xVYuCIF+S5Wd/huHu0Kj3w0/+FtBvG+ocJCRjg98JwtqwVLY6tX2vUbLenPVjC/raHqT1l7WIJx2uHWzNk/LqGr7pnKcWZvy3eJEyzhMbp2eTAPHr9Ph5K9MTUlppGOVn8OrO/6qusrVG1N3rQMdTi3czcgzSB6fzRw5N2m2ln6gQ6IL1+adWuM6yLg4kWPhaMok1NZ8quHN3JrTqw8+xVT7ZJ+Vv6Y0JkUYWCUwOqBtuE9t0d00uPaizPCXjCkap678qgwgiZFQ5+PqI1qQmokcA/uf3D95ujR+a05sG+KylYb4FpnMWfBj34PUYk5sJVdf4sdxH2lyuVQ7nZJNagbiX/2QjDvOJwd2ViIJiByzzf6UoRFAQHGkO444Di1o/Is95cixtNQaUPFLUovWd7rASpszCqP4NvA467ce6kmo3FfYoh+9MMuIeckkGrhuWqtgxdRDkxz/geuhM4G48Oz40d4pdeHHHAqFPR98Weug43pm3XvrdvzZAIcHpz+PsMPnOVnBHit74eMTTz7LFzx64fSJ9y988Pov79wHHv/ClVi+4K/v9OX16//IrfAF18G/1P9v8f+v9QO3nR2w",
    "eJy9VFuy7CAI3JLGV/IZo+x/SVdeijOZOn/XqpkQGpoGjQDQASLABXONt5MtX8ZfA3AAZeHjrfIzYVYlz73hYRCWTLmC+w2/sUqChDhneq60Qp7mwKVhZ/UsvBOhg+gEGf8rmX3+GhGIpfqFY34vDg7EA3ez8Y/fqRORWYRpceB9yIuZTBAOzK9OnGlT1tWIS2uFj1UHjdN8d2/SuX6HQ9W4Dt8MwL2RsRWmSBx5PPX9Xd9aTQMRK/j/MHBx/NMUHLzJkPhJcFP+VGm0DDPNmktJNWGdTsggrurd220yE8hUJs/DrLxBcNa/+Ju4Cyr1vCUFPWGRj8CjY+ZJja5BLK5G+DjNnfwnEj2mpXixkR/1BN59bcNxWvdJTvvBk5AdfjoPs1YiuHH+ZGXhv7F+YUG0P/zJ0CNqmQwtBpHet21yBSPHMXSB2kC7NJj7d2YR6UbV2Ok+UBd93RnPGOKj2FE9cRXBke3GThwZQ31B+wLhPyhOK6Ht7GgI9+y78BGb2Gu+KJfbcTN/fjNZ5yuCD522nf2K0KHM64z3OC6Ez8a8TspnfmLZKjB/4m22BTqDTYqcvbA5jatYmVv+ZQrOAaWFe1Pf3lq65oWA6/nGq008vvFk8faNZyvshd8ZlW/rMCy2rz0fftZn/LRkL0tY8i/cvxR7yf8L/1n//65/G6EdIA==",
    "eJytVMuCxRAM/SWURpdV8v+fNPIinXtnNxYtTnKcPECk0REzVtTx8Lc9Be9zTsqc00bCPTLiqBeGggwmoggGnrIBN+aM6jzRhQvhgwPbjQqSBBtzdSBCbFjIfzDd9cJv+be2dsbGJZAHKtbx9vCnFQSMMJcX8Ca48HqcLCNjIs1dDuusSsag/XuGRP+nKalGSmP6nzXARbsH5zM0F2ObKUhJ/buIVOclo5j141n3GKYGfO5mHopMkll3oYZtweNMyhwE9ySkJgd1CdBVH4AS0dHB6pmW5yiEHmR7EK6V780Rn+TfxB+ELarMnV8V+cj2YP+DG8fX2eZy/uMzhb6aDah7wFLcFjqWMfcjAktvaClUonbYKUN9vIi5umzPhMK2mFTDKnRbEw7Bm9DmTl+QRZMkuVRgzOpf2AyUdvX0zT7zqpSmrOMV/2mCqyVGC5JkGk7CZ+DHLOlFd05b5xLazJWe+ZHrVlZLab5vjrnjkecvz2zP+QDH3zU/99zMTyTHopkivDLnPCQcJLbTnBXonQqVlklaLo5I+pg/iJp5tcQ/8svB7xH3rHZoqsQZmQjj1SiobPyi8RQ5pAHYa121zjkoEm5Y79jCYZ8jMcg72awBBm9nqUOlebFS4CrkZrBShfcy7apJZbMRiGHGXyPYpTw37q/h4nevunsi9wVyzNKT3et6XRU33cP5S7vEb1bOtH7osiGhtD/x4fm/4Mn7f5ERHMs3f3HRpodP/PDAR0V+ler+xL2V74j/xc8X/gP7ihlr",
    "eJytVFmO7CAMvBKLgfRnWHz/Iz28sE1nFI300CgDlF122aYR5/JjA4gf+p/w1vuGWNFthh/ZBfpUvvFoBq4gRjXQmzxwx/tMjoQ3jgjLv0e1RBsxacxMFBNvbBL9halImHrgEqKk7p/EvJuUw7/ft3Sh1fwuphhLDG9vMPtFd+DdAZrFmLhMdHMfeGcDVzAWSR5mJRSPRJHRWUlHUsDDJFmTHKWS80pqrG7toKEx0//Acz8VZ7wj1pK+/Xteqevj+NesiqwkyYaRsZ1eLemG+glWXTZlrFYr1dPLJ7Hi+jFj3gxus4Fcu9Q/xk28DZ+81dmYzX/jphXp2un5OsAwTg6m39ZbwdVW5cb8YLdLahtYKFu/QJq0RprqyCRPatXSRqUynpBWTtg0XX1ce1FDHlaVgDqHebQr6xuI97rbSHqnE/lU6fQ989fX86kSvwWr1FFwDeO8Hui5LXVzcmyVN1JnIedPieirKiwHqh9thCEIFQA59L+L31Gk/MIqDBag4nusNJ+Nbuupr6qsq2l9nEBJpMBNnTE80t0sU6OYX1+XAeI0bNiz+9AeRkv6yTXVRyOb+O1L/jp5kDn5bhKJj/25gkVL4YWuUQwj8zyHM+CkuwWHjVo0FpGjMoy0XBewjiBde+CXVpqtXOtixNeGhSe8nscv3K0osOHwZfhzKr7xx/UHvP5uxet6wcML/sZvX/D/KPVxPen7B2T4Gs0=",
    "eJzFVNl27SAI/SU0icZHJ/7/kyqDhLSnqw/34braE2XDZhBBpDUQJxbUVVD2DdMQSUaseDq8M4w147bPD96Ibf13zE2MC/2Cw5k3IiaRHCqWlWQ/xhYIteG37m9MUyThhRfxv773Y389OFI22MrArGFMwrcyBUd/veKMcgTCffyL8G4ZD86TwJWC4exteV/5d7EPRGH1yZwC9oZtiD1IRdFls0Jc8Q2Xvy2OZtku/DRJfOFTrPphkvrC6QryhQGMHKarIKmMFjOAlzxrrBBrPBGCpKP4yz6tH+aHD/brBA2Evzxy7Rwmylt+5IzmBrWZkHIbWihvrwwrraDC2PzN41aJu2JxDmIq33Qs93sOJx7Ss4Bwa74goY2No/mXkIM4zBY9xdnwhCdkzc/23qEv63D5IXcBmeWtdfEnu1qx9twElsh8NKjTd81pk94uOLJLcScOXiERHbXk7qH2xEenpImPoq7dhTR+6JNnwGSbTlfKZdIbOnd9wmbVkmsQgQ9dastcmqfaV37byyzsR/b2X6o+SUr0JPsgDKR2cNiF8SPRORBgN7ROOZJNlzF2YNJ5Jh+iPWUArJGic6LgDpnWekWRcbioBgftudQgVxEunTHA9pUAHYAyPaazzxQryDDTDoZEJQR540li6Rs/0dRFR6pm/dFZnOwmQFjdo3Nv+6R6xJeo8T08c0j5rZX6m+EH5Yfp8RLUP/D5GbdhH74jvxH9sv7V/j+vLwxHGqU=",
    "eJyFVW127SAI3BIavZqfGmT/S3ryZfT29dTTNpGBkSFIiXgN/lPnLwDvEvX56J18If+5GY/8BhyAVNSOr4vGI8i7hxeijz0VL1W8P7SvTHHbFX3EsZ3/OKjEfbzbzGw7bljuK7OLwsnfpwmLujf58XWJVhzvkYkZVzmSPVUmn1X4lKUHxVC2GtyH1FvzG+ZThPF+9Q/5FleJ1JvS3ezix/LLTLFMcDBPs1LCF39LVKyOlY0L/4ihtE531fi6RQv/dBkz9oJleZuBXRmf8cF0hCMeJIXniRSS4kB79UEI22wz4UfJPj5Eh0ttQJHxKh8z0xceAzyC32gS3zX4QAiXtNuDR3Ucb9Mk+O3dpmn7LnhEsH7byiccl+2Pk98VPf75AtDMXhFQwkbWuda74P0ACqxWtvxm7ppS1Ien4y6frzZlFjRHnEnBXhG9Mn6j9pSHKy9uHktE+/LuL76nMrLZxkkt+0mEyEyz9uUcCa4UPabcfEY5tW6cuTG+ho1cuy6TQu8IT7Q9NOv59zDx0VVEvbH2hTSraQnViKNKNaVBmJrqf09fLRPE0MjGjhQOnX+4/knRJbmLBa2e7SpL8Nr45lzssndCybbBzKll9hUINb54T/NNAK6W5Q9aO0gsbm5AJge/aNNUlR0z5wfaqYmERAitw9KwAQCPlSvpJ7EOq1FjCGSkClf1ePmv4rNPJkPYQvUl+e0PK7U1rpP45OVsODrexcfo4sLzHn9MJzoNYWVxrGXI/8dXvCr7MSPWsP8R+ZvjL6v9gf/B/w89BhlE",
    "eJyFVVuW5SAI3BI+Es2nGtn/ksYCNCb3nGk+0l6K4q3NTMx8MzeGhANfPUM75GITaHPGyU1VTUM1f4i58Ik3ycvTkOLx9Y9CJUlsMEn5klDV2JW543vC/YMHaB8/ehJ+ITg8N//LjFDETeJwKO+Hn9nP4yUxKyLUjXxM3DzfiV39FLrhaYMq2AsfwYv+PdoyPB7/xZreOHVLG8bL4WETCpqbtuHd0ar+68ETrBw3/82MgvIl2Jpasloje1I8Y+b5jaeeOFTFG1Jc/YvqfzSP/Mq/Pv41bu1R4yRZqG1cUfuTIueu5q+Fwi/kkhqXa2nCC3dav6yzJDd3GnJqz1NiD5abJK67i+Soyjopk/YG98HxwXd6WO8UHVJ07IjnfOMOdymBdF3tNt06iT5tyrxl7bVKS66ZED0c1rWVlOus+Km8TwraS3OeuI1p40+3pFu6VaZxjoXzB38ZfvHVP4uVFy+ILmwzLF+H+gb0j/berXHHuh2qmpr9MY1hf21Uw7WTDSu5PUXf+NhaATPO9w8O9eSlVRjEdcvylsBhJW54FRwr17GcBYCzSIJnfUC4XlZaUw+2IfFEwIE1Gd61CjP/8nrIqxYtkVPHbG32xfjjRgzHN8+rbPxIxsd1JDTKVsB6WQ6r+XKI1JHYLEnyr+aTZMZt1T9fhwuVkK7kCa9eO2j8XBBwYIdH6Gb/ABZOpzUDr3vD9X6eHWuj+ZfS5Rw3fJhbJbjW2tX9YdeajUDKim/8/gOPGx4tp10if4T++/OH8IP/xZ+Kf4tBGXA=",
    "eJyFVEmS5CAM/JLAi+BoDPr/k9page6JGA6miiRTO0SdeJ1EyPvBn0zLavIFovFt+OpnTLwojsJPlRmwMl/ns3Su9Hslv8lWM1NHc33swpxyg0XwCTKK54uzQyWN/6hlvoZy1jnadq18XhEOJPWkb8Hz0hNgtbaZ5HXzTb4BHMSAsI7KDBnhl6mfw0yXRPgadtoCP7ZAL4UQl7MV72q/DtVq/D12PjWU/DJ4MR78YXnpVCXdJt0XcjevnmB8xhwvFF5PdwZF1Uy/D7WfpTXStP/9Y62e6b5UBtlodCWIifrpQFPxxCdulqvB/HFqOTwFgWvSKrcJhOI9kwPqegcaRcknrdUBkWjffrP+KyfLzBS9/X76PfKHG/8LcdRCme1kSebZibYrpRVtF/UM2i/8aNAFF5E5Jo6PD7wgwv2Dpxda4vjO2f6Xdoas5IyMgod/qJK5Gq/Qikech9dzTuu2Tp9SaC6NZHMqo+T2j6m55uDDPTLHR1su1dN+FfzD5SALeNyvHxexH3+9o3XKcIltHTt/PXAx8bjnankrnRta/vk0yQu3zGmb3uozIpNzx3vlPacNpDWWdwi3wIZNs93HpZYq4/WrjbvtCcdtq48Zk65m+/OBm9c4P8PS4c+3udFMP6FB95aGq1qUl8dkrWMzd7wmlk6+0wI3/ZJNjFv2ZEPXkhfSKeVk4G3vlBXWZEDcAX39kyeS5pYd76yZAzD/4XVcosfArT7lMLxIznIA3uExm6KxT+rip+DPf/B/8feXc8N/AAzYGLM=",
    "eJx9VVe2rSAMnVJEOconJcx/SI8UQri6Xj4s7JSdptBrJzl6b3S/6VK6CRAypCpOgmHhl+LHxOiSvX1VvSXY3Et/VI9NQ6SXJEhkIvfEGWFqp7dPHr8ozpmFhtCWRxA3F/E8H3W6MeezX5lPkksTz/dUrJya8S8rsigJGZe/4eIzM/Vg/tGBlDoQnpgfNjQf1hAgb8gu77v7NOTlIigHsVllTtPFAZI/JYFozgtVygqhqqMzRSt9Us5x4qiBt+g/Nx/qQlk31izaaJGHjnMv9a1u5RlWF8o5T6dNXZXQWHS2uHS46EQN+3S8J7neV/yZCEr8xg1z/js3rQ3/AYRfpKDW6CKjkVEajV14+EEoEjUXCV5oAQy/WCWOO+OVTQ3lxyJh4i32jxtTxsfBPfpXH4kf/uwcEyqtA/k5+WTHKWwZ/KgUB85D3FTGrmSwciX3UeAUGozdv/pc7ZD8F4LqN2YVllfw5rJUiq9t2ySBDeJLuP3z/Py2r1X5BDSbKVzeOQZg9qZCxXpm/LBlbhJmRs8nLJ8akvi2JxN4230HUvm5+rb/Ke5hTJJ7ztuReENdEydbZ3zMtdnbmX2XFageT65FzTvWsNXp43YTt8ebn77HiVv/2odadiVQXDtofzjbkbjdzmlv+W2FUzV489cy2R/MaOVNTWgEtyPwcQP3E93x8LIP3/Z//Q+1f9LZHbY=",
    "eJztU1u2pCAM3FIEefgJAvtf0pAXRE+7grlpjzQpU6mEACMMNBhsfb3YkqxZtgYia8PLauKN5VEtTwqWlPLetDr2dnxVt/Fz/tCKRJ0vftXtODXJSMXiB60HY/Vdn6oWngPrvG8RrZGIc4FA0vwCmyoCbgRQ6sjgRW+uD9gXksmf6A9mpHTYmlN0RPmsc4VJexaQra78UeJJHJJ0qjYbeXuDkO8sydSnoSyT1MCSf20exj03wbaxr4InhN24ueW9MG/f5Uh9B5e7ZdRV87bk/ZoUvwftJUi+fUdXfNo66Otx5lwUqlNK6tGausZnMWfdVRMRFO8rfwtLX90KogxFH5ckOPCx+im4Dic8JwbpKGM1jnmaTHIxI0rZCibc/BS0rkYnramm0eROADKu+Egprvld6JwOHh3lXZtricuTH3jlgktjOX7YiQK+zj6u84NH/4H09dbGjaxZncZmaPHA1y1rC4zhrk/8tqTGMl7liaOX++Ie+DyQeAp/Gj/NaW/rB64duT9wzRh+45cqht84qD9+4Mqff+OH+j/484f/z/4n+wdTxyC2"
)

animation_ = tuple(zlib.decompress(base64.b64decode(picture)).decode() for picture in ANIMATION_)

DURATION_ = 20

def getBuzzerEvents_(buzzer):
  coeff = 2 ** (1/12)
  delay = 1/4
  previousFreq = None
  
  elapsed = 0
  events = []
  
  while elapsed <= DURATION_:
    while True:
      freq = 150 * coeff ** random.randrange(18)
      if freq != previousFreq:
        break
    previousFreq = freq
    events.append((lambda freq = freq: buzzer.on(freq), delay))
    elapsed += delay
    
  return events


def getOLEDEvents_(oled):
  elapsed = 0
  events = []
  counter = 0
  delay = 1/8

  while elapsed <= DURATION_:
    events.append((lambda animation = animation_[counter % len(animation_)]: oled.draw(animation, 128).show(), delay))
    elapsed += delay
    counter += 1
  
  return events


def getRingEvents_(ring):
  elapsed = 0
  delay = 1/5
  step = 1
  limit = 15
  current = 0
  events = []
  rotation = 0
  
  while elapsed <= DURATION_:
    if current == 1:
      step = 1
    elif current == limit:
      step = -1
      
    rotation += .2
      
    events.append((lambda green = current, rotation = int(rotation): ring.fill((0, green, 0)).setValue(rotation, (0,0,31)).setValue(rotation + 4, (10,0,0)).write(), delay))
    elapsed += delay
    
    current += step
    
  return events


def getLCDEvents_(lcd):
  delay = 1 / 7
  ups = [random.randrange(2, 16)] * 16
  downs = [random.randrange(1, limit) for limit in ups]
  levels = [random.randrange(downs[i], ups[i] + 1) for i in range(16)]
  coeffs = [-1 if random.randrange(2) else 1 for _ in range(16)]
  elapsed = 0
  events = []
  
  while elapsed <= DURATION_:
    events.append((lambda levels = levels.copy(): lcd.putGauges(0, levels), delay))
    
    for i in range(len(levels)):
      levels[i] += coeffs[i]
      if coeffs[i] == 1 and levels[i] >= ups[i]:
        coeffs[i] = -1
        ups[i] = random.randrange(downs[i] + 1, 17)
      elif coeffs[i] == -1 and levels[i] <= downs[i]:
        coeffs[i] = 1
        downs[i] = random.randrange(0, ups[i])
      
    elapsed += delay
    
  return events


def getCommitEvents_():
  elapsed = 0
  events = []
  delay = .35
  
  while elapsed < DURATION_:
    events.append((lambda: ucuq.commit(), delay))
    elapsed += delay
  
  return events  

def launch(oled, buzzer, ring, lcd):
  oled.invert(True)
  lcd.backlightOn()
  
  allEvents = [
    getBuzzerEvents_(buzzer),
    getOLEDEvents_(oled),
    getRingEvents_(ring),
    getLCDEvents_(lcd),
    getCommitEvents_()
  ]
  
  ratioBackup = buzzer.ratio(.992)
  
  cb = ucuq.setCommitBehavior(ucuq.CB_MANUAL)
  
  ucuq.commit()
  
  ucuq.sleepStart()
  
  ucuq.playEvents(allEvents, lambda _, cumul: ucuq.sleepWait(cumul))
  
  ucuq.setCommitBehavior(cb)

  buzzer.off().ratio(ratioBackup)

  oled.invert(False).fill(0).show()
  ring.fill((0,0,0,)).write()
  lcd.backlightOff().clear()
  