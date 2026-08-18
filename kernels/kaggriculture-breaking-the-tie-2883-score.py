# Kaggriculture · BC9 Imitation

Imitation only. The deterministic farm route stays fixed.

The network learns one 9-way residual market decision:

`NONE`, `H4_*`, `H5_*` for `MELON / STRAWBERRY / MILK / WOOL`.

Position and quantity are reconstructed deterministically. PPO / PSRO are
blocked until the held-out imitation gate passes.


from __future__ import annotations

import base64
import copy
import csv
import io
import json
import math
import random
import types
import zlib
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

SEED = 20260818
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

FAST_MODE = False

TRAIN_GAMES = 72 if not FAST_MODE else 16
VAL_GAMES = 24 if not FAST_MODE else 6
EPOCHS = 70 if not FAST_MODE else 25

BATCH_SIZE = 256
LR = 2e-3
WEIGHT_DECAY = 1e-4
WIDTH = 384

PREMIUM = ("MELON", "STRAWBERRY", "MILK", "WOOL")

CLASS_NAMES = (
    "NONE",
    "H4_MELON",
    "H4_STRAWBERRY",
    "H4_MILK",
    "H4_WOOL",
    "H5_MELON",
    "H5_STRAWBERRY",
    "H5_MILK",
    "H5_WOOL",
)

CLASS_TO_ID = {name: i for i, name in enumerate(CLASS_NAMES)}
ID_TO_CLASS = {i: name for name, i in CLASS_TO_ID.items()}

GATE = {
    "full_exact": 0.9990,
    "event_precision": 0.9980,
    "positive_class_accuracy": 0.9950,
    "false_positives_per_game": 0.10,
}

print("device:", DEVICE)
print("train games:", TRAIN_GAMES)
print("validation games:", VAL_GAMES)

%%writefile teacher_agent.py
"""C166 anti-H4 meta counter.

C165 is preserved as the baseline. One addition only: after observing a
high-confidence near-mirror opponent executing the same four-step premium
front-run, the agent gets one step ahead of that policy (H5) on later matching
sales. The escalation is evidence-gated and skipped when town consumption on
the current step would immediately refill that product before the opponent acts.
"""
import base64
import copy
import json
import zlib

_TRACE = json.loads(zlib.decompress(base64.b85decode(
    'c-qxnU2j|05&SQD=7ag65BE*6nOcZq8M0g=H3%a>QxquDhqP}+{(EJKyyU$*J3G7Q&`O`e$mG4}`|Qrn&VK&y+24Qu?bly^JNwh;vk%uFKb~!8XaD&5Uw`}e;~ySB{`&K8|NP}YkDouEefR07FCXsj-hO)Xa5g*Jyjx#C{&&9G&OV>LySZPV1s}ft{QCXPkJq=4zkYMKdHk*U^T&7V^@p?BYX1)(*Xy^BfBtcOd-wiqc0T#@t_kOd*KB{Ejrw!*=7&!oj$SwP?DN@X{qf<cUBibr*SnSuKO34e9*B?Y+uOtIU*pCuabp*58}|b`YUTU8`-gW=jXHeV&654;xSf;t?7FEw`@2s!w{O2Z{_n%5r-Ah!Jo%>H`rGR_>%$<=**o^%1@rj$PwyXwVIRM1n9=XQ&H;PD^A|?z<N9HJ?>+DN19{%=n{X`lEq<Q0(Q|iSVk0rxqUdplrWdBuw*2rouvIdXXqrAej|@pTb+*AD?>_B@8jM6?>g*CbG<^Tq%FG?L&h)>}%nfJU@TN{PrwmD9=A;n`XV5lx=rtIK=Z5DN#J(wql{WoTZZwb1#L2K0)<LfOjq70Fy!CZ@`bj(OIJ6wSto!N5jZFb)c6bY>FtVrqNntOYqG8_A#eQ;kd%J$~@a6mU{lm@e&0n7;*50=%i>R`;Kr_e#_Etcuq27va7@cIZ_vc*C391~F@oy?)mEW#i-tui4c8Z^HKXK<C9nJf(i#Bx$jYoO8)erRYS=9Zvo_p+ebDnbq2lFaEF03zO9Yy>gr>Pg)gm)txXTia+Yk$iTez@y%XEAJ=(h&b#uQp{Eh47%=TQ#*&07Hleq0)}210wC1uz^SZU7<~ffvt><?={H%0n_D-c-TPZ`xef(VQ9)1VC}t5|65Mzv|-zFhm9e=`Q*<ZAMUR=->vWOfBK3FzT5?s@>RIQE#GNT3#D#q7vtnZw+nJsGtm+D+5c{Ay(RaK_R$*6*#`4%$wit0fVJ{Ae(#doCv5fMEW|_9?Ee5%B77$B!{}|@bWueeFz9V|guvt>=oUDA4a)=UpxCRVEp?Ios=;?y53z+}jfvr4ouKup1LE+I31n8ZLnrWH4HeW)3=Z1qmphLtN{$-Yf@&DEdSBHHIdXAH4=mqc#IK$jSZOy<dP~I@iH_gI$gv2mITLCRoH&(V7u@yzU)Jj0L>{vpXfJfr#T5r3t;*BEV>a?IfP-%8lI9w?J01Bh`D4tK?!6wjH!&86pJA`oM!VPbtHr-_8=c_czDv!TY&(OA%TFb7&N>Z;=Snu(0m{=F+?C90PGomD=)sEcs5%g!>aN1n9$93pm4d&HY==S|ADptMbC-ORq#ru#IAgtxjv5Qh8Xe(O5x!Sx80`vDhcR~LB-%|pfYt^$TzbQ8^8BH;#;1?#0bMwrf2TNl?)q_~#m56!XjudV^(3V9xxoqu0BfWC5Modqrb6!MB6C%%Q`5mLNFXBL6oy#lVF<<a2Cw-hmv?=pj!o_?2$P7{%RmRicN>6*31`^D(Z^)<`Q^5JH74#`hAJhP4ABr{7qb%AwKhu0r~r_DA@m?(O72>w0Y@3t?`6Cs><;@FJj3CG-rnDRa3+}8QisiQcXzu>>;Q-KklFEg>AW?^vh9Nf1<<RlTelG1x<zjH>c%AZ>W1eGD@K1Z@fHq`H89oWc26*(eRl#RcO=#syWEs%PaK<tkZr{pd0zUD*MykWl}h+pxVP(~h$uWgb_txzSt3Z{ZAa6}6~Sg+V=~B6?{Z6+$A+ZJ3<L!wNq#yhoPypP`D~5s3DH2BF^eEII!oOwWk(Wl3Y@;!!##;B*=006^XZt(FckpO2;mi-Tusv(0-YxsBSbmpnf(dIgf61wys*F!2x7_0qlMsULrOgG84^$Q3*62GSf<9lflITvQ2?a}EJka+S%bEbH{t??g7Lv@e03QR!<j`a!^60|RqPQqvE=al!_d0m25RXtz;KyKWTfKdPhX4TC;dj-ZUfMSVU4`K`7>@xtF1$FlieYnwWKOlZh@w^DIZLVYI#~yuT3N}q`}t9fXBV8`8PS#HWev7u;|eD3@VVbzkSz6@KmUe;Cf_>>ZwGH|KoFa7%>4GU2HofQAQ3)#`92;im<m~jTn6;oF`^mcPLz&CQbHB9-Ckeh6U0&ffm||!&|*uqd7Ql@4~5h(g=kg1@CaLGYMG=RTEgCuJ_oLJmJ_;la;HiA7Eeuqw(;*VbqP687~utzFRv6#z=ElEqfs}U7~}slK5b^GsP{8JWesY&1K$sXux3@;JU$7@J^?ZZz+zfi3YBVJ#!F(BTd5eKEBvigiZE-06<h)SP&x~r|FG7f?M9j6rHTjN@qEoUFeK<Ma0~)2KoF|Yt*5Ik;;6YY>Fbc>KE8j;6{BlGm%{Ik?~v$Ads*)wTw$9vK%}|ueLMZGgT8@_o0=np5yG;yxbN{Jk-V#WkVuGKz6*A|JFYZ)eeC**>z~YZB+~lGFk_vltn)?HiPuXuNDD)YB99YdB97688$;Zp$=d(lOI@JV3oDREs%wW^v)s=F5cq67Dv+?dX4VjBsE3=1aJQ&Cl>Dx(;shce-LaMbcrD96LeOZ91&}!96y@*E9G37R7%cac}Hhi3$Iu)<8+%`$vuvCQip71%_!~AKgIyM8nfI^ZI~+^^}3E^PB3+Eeo<mEjg_4*JAwNPC+4pE0XF6cVg>9=O+4<2T9EdJps|#z(v<53a4us6fDrgbaE8RM^+%h%9E}+#b#R!xu`AXxvEWG653>Dbu^zF@HQ$-~w7{abSlE$tvNj(qmZf`PQ^jhy{?Y2;-WxUWbw6%Z_T$jv5^Msf6;34ORam#Ir2~XlYI_9aUZKv?iJOc>MIm<PfT(s^Ym-B%HwmY4I>|7YK?JGMsM;P3Xew|-oa~i#oS(2WM4s_dCun~~D5Fkw4MAJT>XSzlJU_5C`HAyq8Z{#_^f4t(VLC8Bn?+!0NZQ3z!jO%ind~oXcWCl>B#W00|2V9D;ONsXP1pH_zm(6(4!G#Kpc#^rThP>e%nns)x#A;;uR&_ufIT`n0qHSjfd=Jl28+<1HI}gnI}!j?n$Mq<X;W7oyI$-`=$^yWCM|@#(1j1y&2R_+cRp$|!303z4JBSV94PvNW20r;1>sL0zhKX7(%bWnBp*Bqml83e*(3wB(K+1%-j~J?_dCd<>I&$jEVM%HkXfe>C*s{I>+%$6n4jAwz+u+F%IW~D5+q2}=qg6kh;5;!Fm$W6B{kS8G>rVs3te(IMW_Z-ogiM{4aPwTr53vP(}cR~JqMQ%jK3Q1kb*CXF>I#Jk^B#;G71+#A(rjt+NGBzkJ4ILugWe6J$ZuIQb~^-c{<5L;4m4{o#Zelib5@7+lFBTcGFOtJA-)JhFE4LGg|4m=9FsYi9w28r_@FPXJskNl8vTzM?kE-LY$zKZ3%rKhO|hnN=o!He3yhQ+!BvPeu*YBmi=JPn3}LEbCzjU72djnQb}L;q8mF#r}ut?fhe$5I;1}SAGw#b;VJz)%((^;E+lU!dY8l3jxYCx`!93d{k+okKA>nH;8Ifnl#()A3hT&;njR6e*pen*IJ;9$>@lNG%Op;f;L(y4h-WY1a9G23_>maofGb|oiU3ng-QtX`C+jF;4+oMr35P2|$0h>BB$FxPZ*pEyKivzus96Lm=9?)ANpXOU>VAZSM>l+C&)W5eDpB}eEJ(kgte2*BhxY*RHDG`lZW`u%Ka;sHnhRWkZ6ZuI8c;9y(y<T%p#tmNaTp4merz@}#~=?2!Y#tsK1X!&<4Zz!=upM923a9%rU*=rr1}%$^E0jqI}UT{26i18*%yF<>WLo1)5fz|*#j0s(@Nf0c8aS}u1oEh#%0>3ka(p?Wjw!D7B|(3E;$yO3hC~kTm7Nk*3-m5TM~m4@lK#es>R`Raxm(r(?>mJeNvn^(mSk_N<&U@s09)u3y|laaz<jUMK)FT*~X=wcP=hLG<{fFU#fEHqF>#C*k2=<u^80S#*_qX(3WlHpjK35g4|;gJ<lNcV#+LyzqmoEsx=NCm>^K*-fAC1IMbDP^2A_WlPEG_0sd8;cO)n4GngiS={XcI^1b$!q9j+{lr{}<;jA2VLjw1ao8sp~*`$`fI^MZl<cOdg<q9<@K!wpW{+G^SKIN4KZ6?ACwT`6y3uD1Pt<%-^)FHi=E-Li!a^0#$CT`ayN!pLwH5L5u9}7&?Ao;6MoI*J2yh@CmQ}j}W9c&{t;$7em0Qc^7d!6q{F<-9}&dj@dxiB%#ko?!wPB|v9fr#Hs4O=JdU$zBUIEjV_`^C2GQjZyHB(J|>s!33#hlP(Ic{@NEc61`dpp|oH341gFvtVBH{iB$$?L&at0IXFeaiP;I(j_}WK?mxV6xjSs2qoNPkaK&y*c-0Dw0DN(Z5w&Mq_zc<Dnk`w%o*17b{6PzC0!flXBqolv;;%6ut5ox33szLP6V+F0l+TGSYT8RZ?Gb=l&DG)HlMtsdB%+g+}MI#SP!j|7o}mcOvuR7Q|m>H6vM7Y&E+Ueg}Z4j<pOt;6{Q$+H7Su~CglurYGw~*se->sqh^kO+9+<7FZQl-M5%7ERO<rk#I3evSyx3)mdm46tUu}gETx4tm^$M6&(sNkR#7nbl`UcC6N_C@Lfv4I^w=Ckz;qV4wW(Yal@rGj2R+RvlFgJ8HDR34h`36~d>MR$30{#P7Y!ulf=djGM2akG#TucQT($H&qn1XhG^xUF!78Q$B?ezlgVXWD_;_Rn8=KcZiDP7Qfeb-$l|$|}HQcCko6DkHhqIv~KrK~vQfiGcp_6L+?@a89CJGSak!Y-;Q%LBd3W(q2kV*otG9(FauDnM$FM5Q)0$sd-zH%lRuR%t+5DRY!8TL_<fnMU${g+Ul8UE@VZ~n1D;Y_L+C6xj9(-ieXOVQlv6E_sXnS`My_|e}$$C-J6+2|%!IpWeT9G#J)p9w9!O!XBfti*0x&Dmn+)-iP$K*@0_5mEXg;pa<bR)OOK4MLU;snWw*vf)|nW-S{N#kH`jAiCbI6z)(xm1(fEJ<Fu(O6716h=F1`Ixgq!R~9gr{iKBwGz$wn&VuUYqD(wLqFQkah;QO!h5ONzzAP*nsjv>o0s}EZh#`B&J6@V`mMN1?Y6?X2SnFCiR<&gU&|Ex(;9Ak+*OW&ik`SOldbQ2;hi%p%(2dI~!LvuvaglPJm>f{BhXbKvya~MOo(*uaEzTk*yGB{sRGCf*cb}r(x9u--3NZhS5e*yi(>S_-Xes7PUW;92<Z$24SH}@tukLWBNG+j8w-JG~F!ji%dCnXaRu`!)7E>0oLQ~z-Wxp{GJXwHi1pZ(KL4SsLOV+GR6)$EsCL{i?vk(%RFH46g$es-xh79Mc=xu=nRl*0`)MCPt8n7VsL11r|%QiiS6VRx#-1H=0Dpk^ysRO16ff=MUT-|$YU3$Eb5%n=M6^!LMmjYtKY8Az#OIfDMp&?R{;<%WNV1g#0PU3k?@YdT#iJ8(Q16NgdQTK<|vOu$kF_4%|Ito3k1P2VfGMqYaQ^0<y#<Mbn!Jgc#1!@Qz!30F+s>aPSC}%KG2_8s9=wcd2N8Vh`A(oXWftRK4yz%)Y@R!58S;5}ecoo2VU~@5kp>+?&<EqS;^~a84rdFv*hTuUQqD%I8$a(XUfoBvTAdR}*R;oIWPOqz%WS@6p8N9F>Fss{ahyWD@TS%U5;Tdf@(YYn*9{Ff3x2l7%4;VUjl5#D|K8>w;Dxf2>R&WTWcc~JiCFn&cVNR?!7XVXrv@s8y`Levq=Lt2nDX1D|@Aehb(wY4ce;Zh}adF^NY(@rF_~u3!)2hgst+pkmOSs|iVvplk1^K~whQY=u&omjLv7`&5MsFlZ<4wrb=4wy9bT&4OVUUtF&Tv60>=j9|j4=|~<TpqqNGTvx)LNxE@gV9LJYLnXi4YOMSXp3xk~*N3!Gth?q#Nmlc8Q~PwXK!BbwEX5)IU9R1qfM-hBCEmdw|*E_J|;3;_=E1c(^VjWJndDX!e0rFsT;*fU4fMfNrx2@n{9VetA`~RJEnvc?a!rWna^)lvcnFCZCM&<O=8!;$HP_6@(*|xt@-8S45#VX?~^D%&vI>QO++@@(Jz{CNr8#IF+L0x`GuN`F)K^>df=(;kthTQyXzEfS%4k(v6YNw;upyK9cHYG<hJZyXp;u*S%AzqVWhkNyisUq}CErLl<d0e0r49SHlWaO~P5A5@O7tBQnhb;TxY(j)v}}s>bVWs%ofhx?ZV7%dK*2<8~6>i)y85c{4N%iR1_INilhlFp0IX%qzRi0|gK%lZ@1v@p9v=15&vJ!C6esF0GDUMu=Ld5rKJuunH4JJDnJ?mSGXom=zZ>UJ|<1LK7(h+Dy&J3c`6s4im6(y}>Em@pKXhVhe8&yt~CB-5qy?N`{p-x65!;ap3y0XQ)_Y2Ra!E;GnKhgd)eRuuYjRpj(8XpYTLu4uM5Yo}r@nT)fy;3U7^QBCm{)-$fdT0mSA2q$$-ssAeWKYFMl;{&?#498fwh3RBcV)v}&op0W~`cP(z`gPM_0ER|ned0ll$49MYu>3%hF>PUW<95Cdatr<bid7sEI3!|8U=gO{dNgNQ*<@)ySJ*Z8)QMg}$VU(uJX!c5za0SUiwVMh`oKZb@F(#dw3Q5#LDyqh^pB>l8u{nEivWlQIV!O0zzJNa+c(Z2EzzQH%(QaDji$pDNQDjG}4##5clOrY}3YCD7gd5Vk!5~GFRAR<QGE1xQcAZw`!7AE;u$Abtvx7zGfh`u#x)6{A7~ftLuXNn{woDR&5;m0%9p*7yXPkxWBpHOOEn-`1%SE!8s4!zT|IO>qv?ZKQ<w2=DFE9u)#?o4)r6^MW;MbUaGj1BTtWqmZpxXceO>)^m=7<de1OhMI_sU2`GeJ}sxmE>;+3o9C+BP$2laJyBmm*OX5wT#PQZfzbC^=HBzN+P9S(1?+|K-V_Vj<4m^>}X3q}SU-$GDn`?SGh<HJVyKw~i>l*i#rNszBUm(G1Sbua1XvH^i$>JgHjgQN~xS18y-;FQ$IIx!df^mLP%i)727Ls71D%*s5Zxz~*zPsTWbJ5BCO`?NNFQ|7OhGY8A4Gij+{{KGHlA$DJxDcNV&U{eXujmte(Tc;ZNWyRs&Nh-S>Ym(}6nuH@!RA}5MJs8;Di%Hs@Pyq4rz8Mxo6c6Z=cvz{GQE!&ZJm=W$0d``4AgCY<?+?LxoRsNfl%o*hU5?Z9?fa0YTohR17|L)Vx?b|Pp_Q}Ji`&j#rr|FOmpu}?dAOSY;<B#90M;1&<=Eu4Opr!jkFXe3Q-hhr0a?inFXn;qOQCC>OpaMazP~AK-3V22*`d1FJbgAh}knX_ejWoB#QauvbLo%HqR2YRH0O+w_<zrjLaIP~lny;+WC#dhi=@-gJsRw#o<SJR?aaSs6RSr7iRW(eem?jy~le$V21Tp=MW-1d^Vj@o*ryX-dY@;d_f|5vkY|5)%mTITfztOWOIQ&GoUL+hi(Hon=UA=0?XO^$NU8&bo@}f>rpl8`Xvo3`N6e&y`PKoL0KJ-$|@gXuKBAimunwWRs9kHS}5tAsPog&kS^jf64Os&t}56`8mt)6*D!`z_{-lo_w3)u*EKXJpC>F7uxNNp=2K{*p)3+fY)6rk#cK_jFq4=cqg8bp5NEI2ReBT<ttS$?wwEM_Ylc;<SpAxaIipd3g=>yZ|=AbD6p14ucV+^|SXNzbxk^T^6une$D_Xj3JhSaKTy3K$OabOc4BPYEoV7UfAcPNJmXYl>(gi%w#0E3oT;-wVX8s+2NHl`EBtkbz8?+>n`d##B{E4Q%3RhPEA9PNLQda!8qkOl2i0I;gB2h0-ThY&b6vyLw6IwYl6#B|*uNeCp-co>v`P__PbP1Z&J*K4~QrW=N60XpVAL>j+smLB$g<q)mC$d`SK%g;LZqa1mFmskRClH2oT*t~UCb2_7aY>YQ&Y;d6+1D5kAyLo!Bd!rPnjRA&vLc<ilE@fqgqI{`s8bbaDvm?%XI$LEt$G<La)p=F7B*r$M|Q(G@`Ad*#FV;c;F&xwn@A)Ho`KO`zMY}VZiP<qa=&bX$@B_iBaQFILhw(#U|5?Uw>!KH~r&6|wUf@Kqld=kcfXR2t)?JtBqodqVB4GnNBYDSR^nnWEkv}<$`;|)l%s3Zc@V>CJ&Mmnfh6+#Eo{o@u2;zQWSk^`W8w50%KhTcmlKh#kvo(=wPq7dLw9-~v5HdsT!!c$VwjqYe|5<xDGfHVg67OkAHU9N7`sGPar?D~NmYA`E>Knj}8?2BoFc@@bg#tg_|m&rx8GvFVm-^u}>im0>2hd?uk#<FdyTJ$_F=yfs?V+BehC4Aembef7T`RLfPScHkDH7fZk#hObQ{)Z?A(}KoDScjr$6LqP3&Wu)RDWy%)A5_D3YZP)pu9&EgQ)JyU+a|hjWhGsAvt=w-US^5grJP62eR7d`v)t;WWUhbfo(HU%S+PjD&=Qn|m~zF4mKbrFTk)r8YXUoq31+~vS8;(@NbObZfO(oOv1FkP(lE_QF`M)}L(rmchKpW}Ds&=ip-*--hnk}4U8nN5d@MA~;ew{MPwG!@!lhF9B|=ON$rQX`8^_>$_12;S!bV8yPiq6wdR(KkV&!OIuQE!~o)T}3Du;ITRHaE#15MNmb~$Mo`A4Ei)mot~kn&|>dLcx~2xN8?t=NJcsQpeGCe3~jw6vuLzRn1PixL_n)DJj8Uh-{>S-t92ElO!HO~7Wh#3Dz}sgPO5NM6UP%_o-AZOkiKc~Gvxwpm7ml_q2%Su|NB(@=V+-Z&|kA5dk)*10C^2?#MP+XVJOwqBFPw&sa+4n*To8UGZiV#Zf<LR5n1B9b5MHPEXvlFzdbIMN$EzEX&|oI7gi9Xx1FmtKsJixQ_Yl70#LEk~cy`CS4Hi|~|aCGUjvTs9$v7Ft=0QRWPb1{h9c1BDQW64j3lz>GA~T*4iL0_lEnr2xx60ZoI@-Q`+Vn)}OqpEeE#M{Psok`Fo)1DC}dmhlNgVW=o6pQ#T~qGK_H&B>$Stjp%b={3SG>imxlMeo3wSQ55P@6a%L0G>I4f)}IMlOvMrGUpal!%@SSE$m#UggBDb=v1AXxf3Rqej>O5*dcnMQ&vTcDX>z!F%}g@`A~{1N#1Z2r$|sjuGLFQX=0?IL<XFd1wTSOkmN(1EJLathv}y8u?(3Wl<BD5POsy*m`v(O)+l1n4cooicGe5g272Irt_z}4r<D&8*{<w1(mS)<zMSHSG*KjHs7N)@80$1YI}){QM5TyP#Y4wopqN5X1r<2jE{jz<vh==lP57u;(uP>z_q5U`Uh;{GSTRuQnXjajq0uQek;KVHm_r4JDnd;h#nLo00?f43z_11kFTY0*KeU}oU<RERdo4}Wfua+}TM&&TC3<-0?jP=PZWQimf)2#R89`^b7^$&eSiPkRoEz1baRhu*72^`;P$KWQmh?d#_=q4x3rkX@tPt8Hpk|N~!8nvvB^9N8;f(XlEhe2mPHL&OQ-fgrcpeyaQiK$xEtJY1!(<V_kCOT#=*DpAmZVR|+@4HZvT7?8VVQlk+L<5rd?|I*Bx(Yhf7vZtMiM*>7%%SkmOikeCwQpYF{CP6QY9q-LPi^2ke(E|G^Ick&2VlYx2T#d0UbM#;)vS`Y#db{n;T^;52&~%#k$A1c6SkuX~i#?uH;6q7^BQb4~l!F#X=no5&w~NEJ+>)=bx#pAL3%>g0gB6ZdzO#?3R{Qhs|3YCX!*uDvsG>T~cYOOeRf`Ax9vjoFC3p9cf}5B_OB?ZwlZQuaZVde=6dcyOcJn20M)oz)hbz0Bjg<qX_o`1i&V_D~c!~>zvgj35<zwCr1ggpb{yE)b|p9A_{E>KLGhzgdU_Q*rGrwVMW_K=4~qVE|}-N2_qHrOj1gi#YS)yTdh4MgERM>NI{;?HijfSSg8my34-#mKblHw2&yc##^fMv8)y!zi$0Eg7lGI|vP0Fhppn<0sF~}b&)pw4v55m84O`uc57)y+W8O-_38!4kV*T=spw*Do_naPi0+B6jaa4Z|SEgll5jEgy<<vQ)J(0bmu@76PoTVlsOV$6!TtqQYiHHnlDd#6QHmTxgXjhb6K`JLACOM)Im2}V*AQnAPNM!pIb)cXfQ)jW6;DcPvY2G-_is7es4mXjjXRc+^cV?qTw;3sUGULY!z@iFN+Vf0WK4o|C1bi`eTTIONgVx^65?z5f%Uy671|!pQjp*qMgfbPWg?$RaOe+XxT?$4mr;$!rTb0z|XpUJ@&@&K2@vG;g{I5m^xvM{vC%!9mZ}LH@o<Tz9yX|n1SYCx!i>(UoDAs}VW#{m6=q=_-Du+gcv(tDRRQQu!Lbe^Q)>F=!<%ln7h)^0i8xW)xpK5|BYAPw#TA)FbQT$b|zLA*E!rd>$pg$cbKJ!8K<}r?awaw&GH;M77WhN_4j2LDKQaX*MRynPF2T;BxTh?`Ui6X5ihME(N%Haj*6?z3$WMHS77BfHMZ4h4vMIe&ph_n^}O^zHBUW?ODW27a8y1->0p?cBC(cjP?rxqMq?@WQ8eM<*X07O7d21+HifwxQ~#j;Gr#;KaNAsRJtGV}Vjw80=wOC;#Px2M13*QODISt#R68glUA%|8K_&6IykV`vMZ`1S5()VCv{Mj~N<6mJThyJg0^D^z17wKaKqoM?eElJWNU?f(F(%jUT'
)).decode("utf-8"))

_SELLABLE = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT", "WHEAT", "FERTILIZER")

_FRONT_RUN_HORIZON = 4
_FRONT_RUN_ITEMS = ("MELON", "STRAWBERRY", "MILK", "WOOL")
_BASE_PRICE = {"MELON": 250, "STRAWBERRY": 120, "MILK": 160, "WOOL": 200}
_GLUT_WEIGHT = {"MELON": 3.5, "STRAWBERRY": 2.0, "MILK": 2.0, "WOOL": 3.2}
_LAST_STEP = -1
_CLONE_CONFIDENCE = 0

# --- H5 meta layer ---------------------------------------------------------
# Disabled until public flow confirms an H4 mirror.
_H4_META_ACTIVE = False
_H4_META_EVIDENCE = 0
_PREV_MARKET_INV = None
_PREV_TOWN_SHOPS = ()
_PREV_ACTION = None
_PREV_SHED = None
_PREV_PRICES = None
_PREV_STEP = -1

_SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


def _public_signature(farm):
    """Compact public fingerprint for detecting a mirrored build."""
    counts = {item: 0 for item in (
        "COW", "SHEEP", "GOOSE", "WHEAT", "CARROT", "TOMATO",
        "STRAWBERRY", "MELON", "PASTURE", "COOP", "WEED",
    )}
    for row in farm.get("tiles", []) or []:
        for tile in row or []:
            if not isinstance(tile, dict):
                continue
            for key in ("animal", "crop", "kind"):
                value = tile.get(key)
                if value in counts:
                    counts[value] += 1
                    break
    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands", []) or [])]
    return (
        len(farm.get("hands", []) or []),
        tuple(sorted(farm.get("unlocked_quadrants", []) or [])),
        tuple(sorted(tuple(position) for position in positions)),
        tuple(counts[item] for item in sorted(counts)),
    )


def _signature_distance(left, right):
    distance = abs(left[0] - right[0])
    distance += 3 * abs(len(left[1]) - len(right[1]))
    distance += sum(abs(a - b) for a, b in zip(left[3], right[3]))
    if left[2] != right[2]:
        distance += 2
    return distance


def _update_clone_profile(obs, step):
    global _CLONE_CONFIDENCE
    if step not in (4, 24) and not (step >= 48 and step % 24 == 0):
        return
    farms = obs.get("farms", []) or []
    if len(farms) < 2:
        return
    player = int(obs.get("player", 0) or 0)
    distance = _signature_distance(
        _public_signature(farms[player]),
        _public_signature(farms[1 - player]),
    )
    if distance <= 1:
        _CLONE_CONFIDENCE = min(8, _CLONE_CONFIDENCE + 1)
    elif distance <= 4:
        _CLONE_CONFIDENCE = max(0, _CLONE_CONFIDENCE - 1)
    else:
        _CLONE_CONFIDENCE = max(0, _CLONE_CONFIDENCE - 3)



def _sell_qty(action, item):
    total = 0
    for order in (action or {}).get("market", []) or []:
        if (
            isinstance(order, list) and len(order) >= 3
            and order[0] == "SELL" and order[1] == item
        ):
            total += max(0, int(order[2] or 0))
    return total


def _trace_sell_qty(step, item):
    if not (0 <= step < len(_TRACE)):
        return 0
    total = 0
    for order in _TRACE[step].get("market", []) or []:
        if (
            isinstance(order, list) and len(order) >= 3
            and order[0] == "SELL" and order[1] == item
        ):
            total += max(0, int(order[2] or 0))
    return total


def _town_demand(step, shops, item):
    """Exact default-configuration demand applied AFTER market on `step`."""
    demand = 0
    if step % 4 == 0:
        for shop_name in shops or ():
            products = _SHOP_PRODUCTS.get(shop_name, ())
            if item in products:
                demand += 2 if len(products) == 1 else 1
    if step % 24 == 0 and item != "FERTILIZER":
        demand += 1
    return demand


def _remember_market(obs, step, action):
    global _PREV_MARKET_INV, _PREV_TOWN_SHOPS, _PREV_ACTION
    global _PREV_SHED, _PREV_PRICES, _PREV_STEP
    market = obs.get("market") or {}
    _PREV_MARKET_INV = dict(market.get("inventory") or {})
    _PREV_PRICES = dict(market.get("prices") or {})
    _PREV_TOWN_SHOPS = tuple((obs.get("town") or {}).get("unlocked_shops", []) or [])
    _PREV_ACTION = copy.deepcopy(action)
    _PREV_SHED = dict(((obs.get("private") or {}).get("shed") or {}))
    _PREV_STEP = step


def _observe_h4_meta(obs, step):
    """Confirm that the opponent is itself executing C165-style H4 front-runs.

    Premium products cannot be bought from the market, so their public inventory
    delta decomposes cleanly into our sales + opponent sales - town demand.
    A signal is accepted only when:
      * farms are already strongly near-mirror,
      * our previous action really performed an H4 pre-sale,
      * the opponent supplied a comparable amount on the same turn,
      * no base-tape sale of that item explains the timing.
    """
    global _H4_META_ACTIVE, _H4_META_EVIDENCE
    if (
        _H4_META_ACTIVE
        or _PREV_MARKET_INV is None
        or _PREV_ACTION is None
        or _PREV_SHED is None
        or _PREV_STEP != step - 1
        or _CLONE_CONFIDENCE < 3
    ):
        return

    market = obs.get("market") or {}
    cur_inv = market.get("inventory") or {}
    cur_prices = market.get("prices") or {}

    for item in _FRONT_RUN_ITEMS:
        # $1 floor: inventory no longer identifies sold volume.
        # Ignore that observation.
        if float((_PREV_PRICES or {}).get(item, 2) or 0) <= 1:
            continue
        if float(cur_prices.get(item, 2) or 0) <= 1:
            continue

        target = _PREV_STEP + 4
        target_qty = _trace_sell_qty(target, item)
        if target_qty <= 0:
            continue

        # Accept only a clean H4 timing match.
        # Normal / nearer replay sales are noise here.
        if _trace_sell_qty(_PREV_STEP, item) > 0:
            continue
        if any(_trace_sell_qty(s, item) > 0 for s in range(_PREV_STEP + 1, target)):
            continue

        own_requested = _sell_qty(_PREV_ACTION, item)
        own_supply = min(
            max(0, int((_PREV_SHED or {}).get(item, 0) or 0)),
            own_requested,
        )
        if own_supply < 2:
            continue

        demand = _town_demand(_PREV_STEP, _PREV_TOWN_SHOPS, item)
        observed_delta = int(cur_inv.get(item, 0) or 0) - int(_PREV_MARKET_INV.get(item, 0) or 0)
        opp_supply = observed_delta + demand - own_supply

        # Keep mild quantity drift; reject unrelated dumps.
        if opp_supply >= 2 and 0.40 <= (opp_supply / max(1, own_supply)) <= 2.50:
            _H4_META_EVIDENCE += 1
            _H4_META_ACTIVE = True
            return


def _h5_meta_counter(action, obs, step):
    """One-step second-order preemption against a confirmed H4 opponent.

    If their C165-style policy is expected to move a base sale from t to t-4,
    sell at t-5 instead. Skip the attempt when town demand after our market phase
    would refill the item before the opponent acts on the next step.
    """
    if not _H4_META_ACTIVE:
        return False
    target = step + 5
    if target >= len(_TRACE):
        return False

    orders = list(action.get("market", []) or [])
    if len(orders) >= 10:
        return False

    already = {}
    for order in orders:
        if isinstance(order, list) and len(order) >= 3 and order[0] == "SELL":
            already[order[1]] = already.get(order[1], 0) + max(0, int(order[2] or 0))

    shed = (obs.get("private") or {}).get("shed") or {}
    shops = tuple((obs.get("town") or {}).get("unlocked_shops", []) or [])
    prices = ((obs.get("market") or {}).get("prices") or {})

    choices = []
    for item in _FRONT_RUN_ITEMS:
        planned = _trace_sell_qty(target, item)
        if planned <= 0:
            continue
        # Town demand can reset the price edge.
        # Skip H5 when that happens.
        if _town_demand(step, shops, item) > 0:
            continue
        available = max(0, int(shed.get(item, 0) or 0) - already.get(item, 0))
        quantity = min(available, planned)
        if quantity <= 0:
            continue
        price = float(prices.get(item, _BASE_PRICE[item]) or 0)
        priority = price * quantity * _GLUT_WEIGHT[item]
        choices.append((priority, item, quantity))

    if not choices:
        return False

    _, item, quantity = max(choices)
    # Put the pre-sale first in the market queue.
    action["market"] = [["SELL", item, quantity], *orders][:10]
    return True


def _front_run(action, obs, step):
    """Sell one premium line immediately before a clone's expected glut."""
    if _h5_meta_counter(action, obs, step):
        return
    if _CLONE_CONFIDENCE < 1 or _FRONT_RUN_HORIZON <= 0:
        return
    orders = list(action.get("market", []) or [])
    if len(orders) >= 10:
        return
    already = {}
    for order in orders:
        if isinstance(order, list) and len(order) >= 3 and order[0] == "SELL":
            already[order[1]] = already.get(order[1], 0) + max(0, int(order[2] or 0))
    planned = {}
    end = min(len(_TRACE), step + _FRONT_RUN_HORIZON + 1)
    for future_step in range(step + 1, end):
        distance = future_step - step
        for order in _TRACE[future_step].get("market", []) or []:
            if not (
                isinstance(order, list) and len(order) >= 3
                and order[0] == "SELL" and order[1] in _FRONT_RUN_ITEMS
            ):
                continue
            item = order[1]
            quantity = max(0, int(order[2] or 0))
            if item not in planned:
                planned[item] = [distance, quantity]
            else:
                planned[item][1] += quantity
    shed = (obs.get("private") or {}).get("shed") or {}
    prices = ((obs.get("market") or {}).get("prices") or {})
    choices = []
    for item, (distance, quantity) in planned.items():
        available = max(0, int(shed.get(item, 0) or 0) - already.get(item, 0))
        quantity = min(available, quantity)
        if quantity <= 0:
            continue
        price = float(prices.get(item, _BASE_PRICE[item]) or 0)
        priority = (
            price * quantity * _GLUT_WEIGHT[item]
            + (_FRONT_RUN_HORIZON + 1 - distance) * _BASE_PRICE[item]
        )
        choices.append((priority, item, quantity))
    if choices:
        _, item, quantity = max(choices)
        orders.append(["SELL", item, quantity])
        action["market"] = orders[:10]


def _terminal_liquidation(action, obs, step):
    """Replay-derived safety net: leave no sellable shed inventory at season end."""
    if step < 680:
        return
    shed = (obs.get("private") or {}).get("shed") or {}
    market = action.setdefault("market", [])
    already = {
        order[1]
        for order in market
        if isinstance(order, list) and len(order) >= 2 and order[0] == "SELL"
    }
    for item in _SELLABLE:
        qty = int(shed.get(item, 0) or 0)
        if qty > 0 and item not in already and len(market) < 10:
            market.append(["SELL", item, qty])


def _shed_access(size):
    half = size // 2
    return [(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)]


def _move_toward(pos, target, tiles):
    x, y = pos
    tx, ty = target
    choices = []
    if tx < x:
        choices.append(("WEST", (x - 1, y)))
    if tx > x:
        choices.append(("EAST", (x + 1, y)))
    if ty < y:
        choices.append(("NORTH", (x, y - 1)))
    if ty > y:
        choices.append(("SOUTH", (x, y + 1)))
    size = len(tiles)
    for op, (nx, ny) in choices:
        if 0 <= nx < size and 0 <= ny < size and tiles[ny][nx] != "LOCKED":
            return [op]
    return ["PASS"]


def _terminal_action(obs):
    """Observation-driven final-eight-turn harvest/drop/sell controller."""
    player = int(obs.get("player", 0) or 0)
    farm = (obs.get("farms") or [])[player]
    private = obs.get("private") or {}
    tiles = farm.get("tiles") or []
    size = len(tiles)
    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands") or [])]
    inventories = list(private.get("inventories") or [])
    inventories.extend({} for _ in range(len(positions) - len(inventories)))
    sheds = set(_shed_access(size))

    available = {
        (x, y)
        for y, row in enumerate(tiles)
        for x, tile in enumerate(row)
        if isinstance(tile, dict) and int(tile.get("yield_units", 0) or 0) > 0
    }
    actions = []
    pending = {}
    for pos_raw, inventory in zip(positions, inventories):
        pos = tuple(pos_raw)
        inventory = inventory or {}
        load = sum(max(0, int(v or 0)) for v in inventory.values())
        x, y = pos
        tile = tiles[y][x] if 0 <= y < size and 0 <= x < size else None
        if load > 0 and pos in sheds:
            action = ["DROP"]
            for item, count in inventory.items():
                if item in _SELLABLE:
                    pending[item] = pending.get(item, 0) + max(0, int(count or 0))
        elif isinstance(tile, dict) and int(tile.get("yield_units", 0) or 0) > 0:
            action = ["HARVEST"]
            available.discard(pos)
        elif load > 0:
            target = min(sheds, key=lambda q: abs(q[0] - x) + abs(q[1] - y))
            action = _move_toward(pos, target, tiles)
        elif available:
            target = min(available, key=lambda q: (abs(q[0] - x) + abs(q[1] - y), q[1], q[0]))
            available.discard(target)
            action = _move_toward(pos, target, tiles)
        elif isinstance(tile, dict) and tile.get("fertilizer_available", False):
            action = ["COLLECT_FERTILIZER"]
        else:
            action = ["PASS"]
        actions.append(action)

    shed = dict(private.get("shed") or {})
    for item, count in pending.items():
        shed[item] = int(shed.get(item, 0) or 0) + count
    prices = ((obs.get("market") or {}).get("prices") or {})
    sells = [
        (int(shed.get(item, 0) or 0) * int(prices.get(item, 1) or 1), item, int(shed.get(item, 0) or 0))
        for item in _SELLABLE
    ]
    sells = [row for row in sells if row[2] > 0]
    sells.sort(reverse=True)
    market = [["SELL", item, qty] for _, item, qty in sells[:10]]
    if int(obs.get("hour", 0) or 0) <= 1:
        already = int(farm.get("hires_today", 0) or 0)
        for _ in range(min(10 - len(market), max(0, 8 - already))):
            market.append(["HIRE"])
    return {"farmer": actions[0], "hands": actions[1:], "market": market[:10]}


def agent(obs, config=None):
    global _LAST_STEP, _CLONE_CONFIDENCE
    global _H4_META_ACTIVE, _H4_META_EVIDENCE
    global _PREV_MARKET_INV, _PREV_TOWN_SHOPS, _PREV_ACTION
    global _PREV_SHED, _PREV_PRICES, _PREV_STEP

    step = min(int(obs.get("step", 0) or 0), len(_TRACE) - 1)
    if step == 0 or step <= _LAST_STEP:
        _CLONE_CONFIDENCE = 0
        _H4_META_ACTIVE = False
        _H4_META_EVIDENCE = 0
        _PREV_MARKET_INV = None
        _PREV_TOWN_SHOPS = ()
        _PREV_ACTION = None
        _PREV_SHED = None
        _PREV_PRICES = None
        _PREV_STEP = -1

    _update_clone_profile(obs, step)
    _observe_h4_meta(obs, step)
    _LAST_STEP = step

    if step >= 717:
        action = _terminal_action(obs)
        _remember_market(obs, step, action)
        return action

    action = copy.deepcopy(_TRACE[step])
    _front_run(action, obs, step)
    _terminal_liquidation(action, obs, step)
    _remember_market(obs, step, action)
    return action


TEACHER_PATH = Path("teacher_agent.py").resolve()


def plain(value):
    return json.loads(json.dumps(value))


def make_teacher_module():
    module = types.ModuleType(f"teacher_{random.randrange(1 << 30)}")
    source = TEACHER_PATH.read_text(encoding="utf-8")
    exec(compile(source, str(TEACHER_PATH), "exec"), module.__dict__)
    return module


def sell_qty(action, item):
    total = 0
    for order in action.get("market", []) or []:
        if (
            isinstance(order, list)
            and len(order) >= 3
            and order[0] == "SELL"
            and order[1] == item
        ):
            total += max(0, int(order[2] or 0))
    return total


def h4_candidate(module, obs, action, step, item):
    orders = list(action.get("market", []) or [])
    if len(orders) >= 10:
        return None

    planned = 0
    distance = None
    end = min(
        len(module._TRACE),
        step + module._FRONT_RUN_HORIZON + 1,
    )

    for future_step in range(step + 1, end):
        qty = module._trace_sell_qty(future_step, item)
        if qty <= 0:
            continue
        if distance is None:
            distance = future_step - step
        planned += qty

    if distance is None or planned <= 0:
        return None

    shed = ((obs.get("private") or {}).get("shed") or {})
    available = max(
        0,
        int(shed.get(item, 0) or 0) - sell_qty(action, item),
    )
    quantity = min(available, planned)

    if quantity <= 0:
        return None

    prices = ((obs.get("market") or {}).get("prices") or {})
    price = float(prices.get(item, module._BASE_PRICE[item]) or 0)

    priority = (
        price * quantity * module._GLUT_WEIGHT[item]
        + (module._FRONT_RUN_HORIZON + 1 - distance)
        * module._BASE_PRICE[item]
    )

    return {
        "quantity": int(quantity),
        "position": len(orders),
        "priority": float(priority),
        "distance": int(distance),
    }


def h5_candidate(module, obs, action, step, item):
    orders = list(action.get("market", []) or [])
    if len(orders) >= 10:
        return None

    target = step + 5
    if target >= len(module._TRACE):
        return None

    planned = module._trace_sell_qty(target, item)
    if planned <= 0:
        return None

    shops = tuple(
        (obs.get("town") or {}).get("unlocked_shops", []) or []
    )

    if module._town_demand(step, shops, item) > 0:
        return None

    shed = ((obs.get("private") or {}).get("shed") or {})
    available = max(
        0,
        int(shed.get(item, 0) or 0) - sell_qty(action, item),
    )
    quantity = min(available, planned)

    if quantity <= 0:
        return None

    prices = ((obs.get("market") or {}).get("prices") or {})
    price = float(prices.get(item, module._BASE_PRICE[item]) or 0)

    return {
        "quantity": int(quantity),
        "position": 0,
        "priority": float(
            price * quantity * module._GLUT_WEIGHT[item]
        ),
    }


def label_from_diff(before, after):
    if before == after:
        return CLASS_TO_ID["NONE"]

    before_market = list(before.get("market", []) or [])
    after_market = list(after.get("market", []) or [])

    if len(after_market) != len(before_market) + 1:
        raise ValueError("front-run layer was not one insertion")

    for position in range(len(after_market)):
        if (
            after_market[:position] + after_market[position + 1:]
            != before_market
        ):
            continue

        order = after_market[position]
        if not (
            isinstance(order, list)
            and len(order) >= 3
            and order[0] == "SELL"
            and order[1] in PREMIUM
        ):
            continue

        mode = "H5" if position == 0 else "H4"
        return CLASS_TO_ID[f"{mode}_{order[1]}"]

    raise ValueError("unable to decode residual class")


def apply_class(module, obs, action, step, class_id):
    result = copy.deepcopy(action)

    if int(class_id) == 0:
        return result

    mode, item = ID_TO_CLASS[int(class_id)].split("_", 1)

    candidate = (
        h5_candidate(module, obs, result, step, item)
        if mode == "H5"
        else h4_candidate(module, obs, result, step, item)
    )

    if candidate is None:
        return result

    orders = list(result.get("market", []) or [])
    orders.insert(
        candidate["position"],
        ["SELL", item, candidate["quantity"]],
    )
    result["market"] = orders[:10]
    return result


def feature_vector(module, obs, action, step):
    market = obs.get("market") or {}
    prices = market.get("prices") or {}
    inventory = market.get("inventory") or {}

    private = obs.get("private") or {}
    shed = private.get("shed") or {}

    shops = tuple(
        (obs.get("town") or {}).get("unlocked_shops", []) or []
    )

    farms = obs.get("farms") or [{}, {}]
    player = int(obs.get("player", 0) or 0)

    own = farms[player] if player < len(farms) else {}
    opp = farms[1 - player] if len(farms) > 1 else {}

    feature = [
        step / 719.0,
        (step % 24) / 23.0,
        (step // 24) / 29.0,
        min(1.0, float(module._CLONE_CONFIDENCE) / 8.0),
        float(bool(module._H4_META_ACTIVE)),
        min(1.0, float(module._H4_META_EVIDENCE) / 4.0),
        len(action.get("market", []) or []) / 10.0,
        float(own.get("money", 0) or 0) / 60000.0,
        float(opp.get("money", 0) or 0) / 60000.0,
    ]

    for item in PREMIUM:
        h4 = h4_candidate(module, obs, action, step, item)
        h5 = h5_candidate(module, obs, action, step, item)

        price = float(prices.get(item, module._BASE_PRICE[item]) or 0)

        feature.extend(
            [
                float(shed.get(item, 0) or 0) / 100.0,
                price / module._BASE_PRICE[item],
                (
                    float(inventory.get(item, 10000) or 0) - 10000.0
                ) / 500.0,
                sell_qty(action, item) / 100.0,
                module._town_demand(step, shops, item) / 10.0,
                float(h4["quantity"]) / 100.0 if h4 else 0.0,
                float(h4["priority"]) / 50000.0 if h4 else 0.0,
                float(h4["distance"]) / 4.0 if h4 else 0.0,
                float(h5["quantity"]) / 100.0 if h5 else 0.0,
                float(h5["priority"]) / 50000.0 if h5 else 0.0,
            ]
        )

    return np.asarray(feature, dtype=np.float32)


def make_instrumented_teacher(sink):
    module = make_teacher_module()
    original_front_run = module._front_run

    def wrapped_front_run(action, obs, step):
        before = copy.deepcopy(action)
        feature = feature_vector(module, obs, before, step)

        original_front_run(action, obs, step)

        label = label_from_diff(before, action)

        # Hard invariant: the 9-class representation must reconstruct
        # the teacher's dynamic action exactly.
        rebuilt = apply_class(
            module,
            obs,
            before,
            step,
            label,
        )
        assert rebuilt == action

        sink.append(
            {
                "step": int(step),
                "feature": feature,
                "label": int(label),
            }
        )

    module._front_run = wrapped_front_run
    return module.agent


def make_noisy_teacher(drop_probability=0.08):
    module = make_teacher_module()

    def policy(raw_obs):
        action = module.agent(plain(raw_obs))

        if random.random() < drop_probability:
            market = list(action.get("market", []) or [])
            premium_slots = [
                i
                for i, order in enumerate(market)
                if (
                    isinstance(order, list)
                    and len(order) >= 3
                    and order[0] == "SELL"
                    and order[1] in PREMIUM
                )
            ]
            if premium_slots:
                market.pop(random.choice(premium_slots))
                action["market"] = market

        return action

    return policy


try:
    from kaggle_environments import make
    HAVE_ENV = True
except ModuleNotFoundError:
    HAVE_ENV = False

print("kaggle_environments available:", HAVE_ENV)


def replay_obs(replay, step, seat):
    obs = copy.deepcopy(replay["steps"][step][seat]["observation"])

    if seat == 1:
        shared = replay["steps"][step][0]["observation"]
        for key in ("farms", "market", "town", "day", "hour"):
            if key not in obs and key in shared:
                obs[key] = copy.deepcopy(shared[key])

    obs["step"] = step
    return obs


def audit_replay(path):
    replay = json.loads(Path(path).read_text(encoding="utf-8"))
    report = {}

    for seat in (0, 1):
        module = make_teacher_module()
        exact = 0
        labels = Counter()

        for step in range(len(replay["steps"]) - 1):
            obs = replay_obs(replay, step, seat)
            predicted = module.agent(copy.deepcopy(obs))
            recorded = replay["steps"][step + 1][seat]["action"]

            exact += int(predicted == recorded)

            # Re-run a fresh module only for label audit would be expensive;
            # action exactness is the critical contract here.

        report[seat] = {
            "teacher_exact": exact / (len(replay["steps"]) - 1),
        }

    return report


for candidate in [
    Path("/kaggle/working/94218844.json"),
    Path("94218844.json"),
]:
    if candidate.exists():
        print("gold audit:", audit_replay(candidate))
        break


def run_episode(seed, opponent_kind, teacher_seat):
    sink = []
    teacher = make_instrumented_teacher(sink)

    if opponent_kind == "teacher":
        opponent = make_teacher_module().agent
    elif opponent_kind == "noisy_teacher":
        opponent = make_noisy_teacher(0.08)
    elif opponent_kind == "random":
        opponent = "random"
    else:
        raise ValueError(opponent_kind)

    agents = [None, None]
    agents[teacher_seat] = teacher
    agents[1 - teacher_seat] = opponent

    env = make(
        "kaggriculture",
        configuration={
            "episodeSteps": 720,
            "seed": int(seed),
        },
        debug=False,
    )
    env.run(agents)

    replay = env.toJSON()
    episode_id = f"{opponent_kind}-seat{teacher_seat}-seed{seed}"

    for row in sink:
        row["episode_id"] = episode_id

    return sink, replay


def collect(games, seed_offset):
    if not HAVE_ENV:
        return []

    records = []
    cycle = (
        "teacher",
        "teacher",
        "noisy_teacher",
        "random",
    )

    for game_index in range(games):
        opponent_kind = cycle[game_index % len(cycle)]
        seat = game_index % 2

        episode, replay = run_episode(
            seed_offset + game_index,
            opponent_kind,
            seat,
        )
        records.extend(episode)

        counts = Counter(
            ID_TO_CLASS[row["label"]]
            for row in episode
        )

        print(
            f"{game_index + 1:02d}/{games}",
            opponent_kind,
            f"seat={seat}",
            f"reward={replay.get('rewards')}",
            dict(counts),
        )

    return records


train_records = collect(TRAIN_GAMES, 10000)
val_records = collect(VAL_GAMES, 50000)

print("train rows:", len(train_records))
print("validation rows:", len(val_records))


def replay_records(path):
    """
    Fallback only for pipeline smoke testing when kaggle_environments is absent.
    Independent rollout data is required for a real BC gate.
    """
    replay = json.loads(Path(path).read_text(encoding="utf-8"))
    records = []

    for seat in (0, 1):
        sink = []
        teacher = make_instrumented_teacher(sink)

        for step in range(len(replay["steps"]) - 1):
            obs = replay_obs(replay, step, seat)
            predicted = teacher(copy.deepcopy(obs))
            recorded = replay["steps"][step + 1][seat]["action"]
            assert predicted == recorded

        for row in sink:
            row["episode_id"] = f"gold-seat{seat}"

        records.extend(sink)

    return records


if not train_records:
    candidates = [
        Path("/kaggle/working/94218844.json"),
        Path("94218844.json"),
    ]

    for candidate in candidates:
        if candidate.exists():
            gold = replay_records(candidate)

            # Split by seat, not random rows.
            train_records = [
                row for row in gold
                if row["episode_id"] == "gold-seat0"
            ]
            val_records = [
                row for row in gold
                if row["episode_id"] == "gold-seat1"
            ]

            print(
                "WARNING: one-replay fallback; do not trust this as final validation"
            )
            break


class BC9Dataset(Dataset):
    def __init__(self, records, mean=None, std=None):
        self.records = list(records)

        if self.records:
            matrix = np.stack(
                [row["feature"] for row in self.records]
            ).astype(np.float32)
        else:
            matrix = np.zeros((1, 49), dtype=np.float32)

        self.mean = (
            matrix.mean(axis=0).astype(np.float32)
            if mean is None
            else np.asarray(mean, dtype=np.float32)
        )

        raw_std = (
            matrix.std(axis=0).astype(np.float32)
            if std is None
            else np.asarray(std, dtype=np.float32)
        )

        self.std = np.where(
            raw_std < 1e-6,
            1.0,
            raw_std,
        ).astype(np.float32)

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):
        row = self.records[index]
        x = (row["feature"] - self.mean) / self.std

        return (
            torch.tensor(x, dtype=torch.float32),
            torch.tensor(row["label"], dtype=torch.long),
        )


train_ds = BC9Dataset(train_records)
val_ds = BC9Dataset(
    val_records,
    mean=train_ds.mean,
    std=train_ds.std,
)

INPUT_DIM = len(train_ds.mean)

print("input dim:", INPUT_DIM)
print(
    "train classes:",
    Counter(ID_TO_CLASS[row["label"]] for row in train_records),
)


class BC9Net(nn.Module):
    def __init__(self, input_dim, width=384):
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(input_dim, width),
            nn.GELU(approximate="tanh"),
            nn.Linear(width, width),
            nn.GELU(approximate="tanh"),
            nn.Linear(width, width),
            nn.GELU(approximate="tanh"),
            nn.Linear(width, len(CLASS_NAMES)),
        )

    def forward(self, x):
        return self.net(x)


model = BC9Net(INPUT_DIM, WIDTH).to(DEVICE)

decay = []
no_decay = []

for name, parameter in model.named_parameters():
    if parameter.ndim < 2 or name.endswith(".bias"):
        no_decay.append(parameter)
    else:
        decay.append(parameter)

optimizer = torch.optim.AdamW(
    [
        {"params": decay, "weight_decay": WEIGHT_DECAY},
        {"params": no_decay, "weight_decay": 0.0},
    ],
    lr=LR,
)


def make_class_weights(records):
    counts = Counter(row["label"] for row in records)
    weights = np.ones(len(CLASS_NAMES), dtype=np.float32)

    for class_id in range(1, len(CLASS_NAMES)):
        positive_count = max(1, counts.get(class_id, 0))
        none_count = max(1, counts.get(0, 0))

        weights[class_id] = min(
            5.0,
            math.sqrt(none_count / positive_count),
        )

    return torch.tensor(weights, dtype=torch.float32, device=DEVICE)


CLASS_WEIGHTS = make_class_weights(train_records)


def probabilities(dataset):
    loader = DataLoader(dataset, batch_size=2048, shuffle=False)
    model.eval()

    all_prob = []
    all_labels = []

    with torch.no_grad():
        for x, y in loader:
            logits = model(x.to(DEVICE))
            all_prob.append(
                torch.softmax(logits, dim=-1).cpu().numpy()
            )
            all_labels.append(y.numpy())

    if not all_prob:
        return (
            np.zeros((0, len(CLASS_NAMES)), dtype=np.float32),
            np.zeros(0, dtype=np.int64),
        )

    return np.concatenate(all_prob), np.concatenate(all_labels)


def conservative_predict(prob, event_threshold, none_margin):
    if len(prob) == 0:
        return np.zeros(0, dtype=np.int64)

    none_prob = prob[:, 0]
    positive = prob[:, 1:]

    best_offset = positive.argmax(axis=1)
    best_prob = positive[
        np.arange(len(prob)),
        best_offset,
    ]

    pred = best_offset.astype(np.int64) + 1

    active = (
        (best_prob >= event_threshold)
        & ((best_prob - none_prob) >= none_margin)
    )

    pred[~active] = 0
    return pred


def metrics(labels, pred, records):
    true_event = labels != 0
    pred_event = pred != 0

    tp = int((true_event & pred_event).sum())
    fp = int((~true_event & pred_event).sum())
    fn = int((true_event & ~pred_event).sum())

    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)

    both_positive = true_event & pred_event

    positive_class_accuracy = (
        float((labels[both_positive] == pred[both_positive]).mean())
        if both_positive.any()
        else 1.0
    )

    full_exact = float((labels == pred).mean())

    episode_count = max(
        1,
        len(set(row["episode_id"] for row in records)),
    )

    return {
        "full_exact": full_exact,
        "event_precision": precision,
        "event_recall": recall,
        "positive_class_accuracy": positive_class_accuracy,
        "false_positives": fp,
        "false_negatives": fn,
        "false_positives_per_game": fp / episode_count,
        "false_negatives_per_game": fn / episode_count,
        "expected_errors_per_game": 717.0 * (1.0 - full_exact),
    }


def calibrate(prob, labels, records):
    best = None

    for threshold in np.linspace(0.50, 0.999, 60):
        for margin in np.linspace(-0.10, 0.70, 17):
            pred = conservative_predict(
                prob,
                float(threshold),
                float(margin),
            )

            result = metrics(labels, pred, records)
            result["event_threshold"] = float(threshold)
            result["none_margin"] = float(margin)
            result["prediction"] = pred

            fp_ok = (
                result["false_positives_per_game"]
                <= GATE["false_positives_per_game"]
            )

            score = (
                int(fp_ok),
                result["full_exact"],
                result["event_precision"],
                result["positive_class_accuracy"],
                result["event_recall"],
            )

            if best is None or score > best["_score"]:
                best = dict(result)
                best["_score"] = score

    return best


# Overfit sanity: the representation/model must be able to memorize a small slice.
if len(train_ds) > 0:
    sanity_size = min(4096, len(train_ds))
    sanity_x = torch.stack(
        [train_ds[i][0] for i in range(sanity_size)]
    ).to(DEVICE)
    sanity_y = torch.stack(
        [train_ds[i][1] for i in range(sanity_size)]
    ).to(DEVICE)

    sanity_model = BC9Net(INPUT_DIM, WIDTH).to(DEVICE)
    sanity_opt = torch.optim.AdamW(
        sanity_model.parameters(),
        lr=3e-3,
        weight_decay=0.0,
    )

    for _ in range(180):
        sanity_opt.zero_grad(set_to_none=True)
        loss = F.cross_entropy(
            sanity_model(sanity_x),
            sanity_y,
        )
        loss.backward()
        sanity_opt.step()

    with torch.no_grad():
        sanity_acc = float(
            (
                sanity_model(sanity_x).argmax(dim=-1)
                == sanity_y
            ).float().mean().cpu()
        )

    print("overfit sanity accuracy:", sanity_acc)


loader = DataLoader(
    train_ds,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0,
)

best_state = None
best_result = None

for epoch in range(1, EPOCHS + 1):
    model.train()

    running = 0.0
    batches = 0

    for x, y in loader:
        optimizer.zero_grad(set_to_none=True)

        logits = model(x.to(DEVICE))

        loss = F.cross_entropy(
            logits,
            y.to(DEVICE),
            weight=CLASS_WEIGHTS,
            label_smoothing=0.001,
        )

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        running += float(loss.detach().cpu())
        batches += 1

    if epoch == 1 or epoch % 5 == 0 or epoch == EPOCHS:
        val_prob, val_labels = probabilities(val_ds)
        result = calibrate(val_prob, val_labels, val_records)

        printable = {
            key: value
            for key, value in result.items()
            if key not in ("prediction", "_score")
        }

        print(
            f"epoch={epoch:03d}",
            f"loss={running / max(1, batches):.5f}",
            printable,
        )

        if best_result is None or result["_score"] > best_result["_score"]:
            best_result = result
            best_state = {
                key: value.detach().cpu().clone()
                for key, value in model.state_dict().items()
            }


if best_state is not None:
    model.load_state_dict(best_state)

VAL_PROB, VAL_LABELS = probabilities(val_ds)
FINAL = calibrate(VAL_PROB, VAL_LABELS, val_records)

print("\nBEST VALIDATION")
print(
    json.dumps(
        {
            key: value
            for key, value in FINAL.items()
            if key not in ("prediction", "_score")
        },
        indent=2,
    )
)

torch.save(model.state_dict(), "bc9_residual.pt")


errors = []

for index, (row, predicted) in enumerate(
    zip(val_records, FINAL["prediction"])
):
    if int(predicted) == int(row["label"]):
        continue

    probability = VAL_PROB[index]

    errors.append(
        {
            "episode_id": row["episode_id"],
            "step": row["step"],
            "true_class": ID_TO_CLASS[int(row["label"])],
            "predicted_class": ID_TO_CLASS[int(predicted)],
            "p_none": float(probability[0]),
            "p_best_positive": float(probability[1:].max()),
        }
    )

with Path("imitation_error_audit.csv").open(
    "w",
    newline="",
    encoding="utf-8",
) as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=[
            "episode_id",
            "step",
            "true_class",
            "predicted_class",
            "p_none",
            "p_best_positive",
        ],
    )
    writer.writeheader()
    writer.writerows(errors)

print("validation errors:", len(errors))
print("saved: imitation_error_audit.csv")


BC_GATE_PASSED = (
    FINAL["full_exact"] >= GATE["full_exact"]
    and FINAL["event_precision"] >= GATE["event_precision"]
    and FINAL["positive_class_accuracy"]
    >= GATE["positive_class_accuracy"]
    and FINAL["false_positives_per_game"]
    <= GATE["false_positives_per_game"]
)

print("BC GATE:", "PASS" if BC_GATE_PASSED else "FAIL")

if not BC_GATE_PASSED:
    print("STOP. Improve imitation only. Do not start PPO / PSRO.")


TEACHER_SOURCE = Path("teacher_agent.py").read_text(encoding="utf-8")


def numpy_payload():
    arrays = {}

    linear_index = 0
    for layer in model.net:
        if isinstance(layer, nn.Linear):
            arrays[f"w{linear_index}"] = (
                layer.weight.detach().cpu().numpy().astype(np.float32)
            )
            arrays[f"b{linear_index}"] = (
                layer.bias.detach().cpu().numpy().astype(np.float32)
            )
            linear_index += 1

    buffer = io.BytesIO()
    np.savez_compressed(buffer, **arrays)

    return base64.b85encode(
        zlib.compress(buffer.getvalue(), level=9)
    ).decode("ascii")


if BC_GATE_PASSED:
    payload = numpy_payload()

    mean = train_ds.mean.tolist()
    std = train_ds.std.tolist()

    event_threshold = float(FINAL["event_threshold"])
    none_margin = float(FINAL["none_margin"])

    learned_layer = r"""
# ---- BC9 residual layer ----
import base64 as _bc_base64
import io as _bc_io
import zlib as _bc_zlib
import numpy as _bc_np

_BC_CLASSES = (
    "NONE",
    "H4_MELON",
    "H4_STRAWBERRY",
    "H4_MILK",
    "H4_WOOL",
    "H5_MELON",
    "H5_STRAWBERRY",
    "H5_MILK",
    "H5_WOOL",
)

_BC_PREMIUM = ("MELON", "STRAWBERRY", "MILK", "WOOL")
_BC_MEAN = _bc_np.asarray(__MEAN__, dtype=_bc_np.float32)
_BC_STD = _bc_np.asarray(__STD__, dtype=_bc_np.float32)
_BC_EVENT_THRESHOLD = __EVENT_THRESHOLD__
_BC_NONE_MARGIN = __NONE_MARGIN__

_BC_RAW = _bc_zlib.decompress(
    _bc_base64.b85decode("__PAYLOAD__".encode("ascii"))
)

with _bc_np.load(_bc_io.BytesIO(_BC_RAW)) as _bc_data:
    _BC_W = [_bc_data[f"w{i}"] for i in range(4)]
    _BC_B = [_bc_data[f"b{i}"] for i in range(4)]


def _bc_gelu(x):
    return 0.5 * x * (
        1.0
        + _bc_np.tanh(
            0.7978845608028654
            * (x + 0.044715 * x * x * x)
        )
    )


def _bc_forward(x):
    x = _bc_gelu(_BC_W[0] @ x + _BC_B[0])
    x = _bc_gelu(_BC_W[1] @ x + _BC_B[1])
    x = _bc_gelu(_BC_W[2] @ x + _BC_B[2])
    return _BC_W[3] @ x + _BC_B[3]


def _bc_sell_qty(action, item):
    total = 0
    for order in action.get("market", []) or []:
        if (
            isinstance(order, list)
            and len(order) >= 3
            and order[0] == "SELL"
            and order[1] == item
        ):
            total += max(0, int(order[2] or 0))
    return total


def _bc_h4(action, obs, step, item):
    orders = list(action.get("market", []) or [])
    if len(orders) >= 10:
        return None

    planned = 0
    distance = None
    end = min(len(_TRACE), step + _FRONT_RUN_HORIZON + 1)

    for future_step in range(step + 1, end):
        qty = _trace_sell_qty(future_step, item)
        if qty <= 0:
            continue
        if distance is None:
            distance = future_step - step
        planned += qty

    if distance is None or planned <= 0:
        return None

    shed = ((obs.get("private") or {}).get("shed") or {})
    available = max(
        0,
        int(shed.get(item, 0) or 0) - _bc_sell_qty(action, item),
    )
    quantity = min(available, planned)

    if quantity <= 0:
        return None

    prices = ((obs.get("market") or {}).get("prices") or {})
    price = float(prices.get(item, _BASE_PRICE[item]) or 0)

    return {
        "quantity": int(quantity),
        "position": len(orders),
        "priority": float(
            price * quantity * _GLUT_WEIGHT[item]
            + (_FRONT_RUN_HORIZON + 1 - distance)
            * _BASE_PRICE[item]
        ),
        "distance": int(distance),
    }


def _bc_h5(action, obs, step, item):
    orders = list(action.get("market", []) or [])
    if len(orders) >= 10:
        return None

    target = step + 5
    if target >= len(_TRACE):
        return None

    planned = _trace_sell_qty(target, item)
    if planned <= 0:
        return None

    shops = tuple(
        (obs.get("town") or {}).get("unlocked_shops", []) or []
    )

    if _town_demand(step, shops, item) > 0:
        return None

    shed = ((obs.get("private") or {}).get("shed") or {})
    available = max(
        0,
        int(shed.get(item, 0) or 0) - _bc_sell_qty(action, item),
    )
    quantity = min(available, planned)

    if quantity <= 0:
        return None

    prices = ((obs.get("market") or {}).get("prices") or {})
    price = float(prices.get(item, _BASE_PRICE[item]) or 0)

    return {
        "quantity": int(quantity),
        "position": 0,
        "priority": float(
            price * quantity * _GLUT_WEIGHT[item]
        ),
    }


def _bc_features(action, obs, step):
    market = obs.get("market") or {}
    prices = market.get("prices") or {}
    inventory = market.get("inventory") or {}
    shed = ((obs.get("private") or {}).get("shed") or {})

    shops = tuple(
        (obs.get("town") or {}).get("unlocked_shops", []) or []
    )

    farms = obs.get("farms") or [{}, {}]
    player = int(obs.get("player", 0) or 0)

    own = farms[player] if player < len(farms) else {}
    opp = farms[1 - player] if len(farms) > 1 else {}

    feature = [
        step / 719.0,
        (step % 24) / 23.0,
        (step // 24) / 29.0,
        min(1.0, float(_CLONE_CONFIDENCE) / 8.0),
        float(bool(_H4_META_ACTIVE)),
        min(1.0, float(_H4_META_EVIDENCE) / 4.0),
        len(action.get("market", []) or []) / 10.0,
        float(own.get("money", 0) or 0) / 60000.0,
        float(opp.get("money", 0) or 0) / 60000.0,
    ]

    for item in _BC_PREMIUM:
        h4 = _bc_h4(action, obs, step, item)
        h5 = _bc_h5(action, obs, step, item)

        price = float(prices.get(item, _BASE_PRICE[item]) or 0)

        feature.extend(
            [
                float(shed.get(item, 0) or 0) / 100.0,
                price / _BASE_PRICE[item],
                (
                    float(inventory.get(item, 10000) or 0) - 10000.0
                ) / 500.0,
                _bc_sell_qty(action, item) / 100.0,
                _town_demand(step, shops, item) / 10.0,
                float(h4["quantity"]) / 100.0 if h4 else 0.0,
                float(h4["priority"]) / 50000.0 if h4 else 0.0,
                float(h4["distance"]) / 4.0 if h4 else 0.0,
                float(h5["quantity"]) / 100.0 if h5 else 0.0,
                float(h5["priority"]) / 50000.0 if h5 else 0.0,
            ]
        )

    x = _bc_np.asarray(feature, dtype=_bc_np.float32)
    return (x - _BC_MEAN) / _BC_STD


def _front_run(action, obs, step):
    if len(action.get("market", []) or []) >= 10:
        return

    logits = _bc_forward(_bc_features(action, obs, step))

    shifted = logits - logits.max()
    prob = _bc_np.exp(shifted)
    prob = prob / prob.sum()

    none_prob = float(prob[0])
    best_class = int(_bc_np.argmax(prob[1:])) + 1
    best_prob = float(prob[best_class])

    if (
        best_prob < _BC_EVENT_THRESHOLD
        or best_prob - none_prob < _BC_NONE_MARGIN
    ):
        return

    mode, item = _BC_CLASSES[best_class].split("_", 1)

    candidate = (
        _bc_h5(action, obs, step, item)
        if mode == "H5"
        else _bc_h4(action, obs, step, item)
    )

    if candidate is None:
        return

    orders = list(action.get("market", []) or [])
    orders.insert(
        candidate["position"],
        ["SELL", item, candidate["quantity"]],
    )
    action["market"] = orders[:10]
"""

    learned_layer = (
        learned_layer
        .replace("__MEAN__", repr(mean))
        .replace("__STD__", repr(std))
        .replace("__EVENT_THRESHOLD__", repr(event_threshold))
        .replace("__NONE_MARGIN__", repr(none_margin))
        .replace("__PAYLOAD__", payload)
    )

    submission_source = TEACHER_SOURCE + "\n" + learned_layer
    policy_name = "BC9 residual hybrid"

else:
    submission_source = TEACHER_SOURCE
    policy_name = "teacher fallback"


submission_target = (
    Path("/kaggle/working/submission.py")
    if Path("/kaggle/working").exists()
    else Path("submission.py")
)

submission_target.write_text(
    submission_source,
    encoding="utf-8",
)

compile(
    submission_source,
    str(submission_target),
    "exec",
)

metrics_target = (
    submission_target.parent
    / "imitation_metrics.json"
)

metrics_target.write_text(
    json.dumps(
        {
            "teacher_sha256": "df4e899ad535754cf2ddbd3c16e48085916b0cd2baa5182a1a2cfc6a856abae5",
            "policy": policy_name,
            "gate_passed": bool(BC_GATE_PASSED),
            "validation": {
                key: value
                for key, value in FINAL.items()
                if key not in ("prediction", "_score")
            },
            "gate": GATE,
        },
        indent=2,
    ),
    encoding="utf-8",
)

print("submission:", submission_target)
print("policy:", policy_name)
print("metrics:", metrics_target)

## Rule

If `BC GATE = FAIL`, do not submit the learned model and do not start RL.

Use `imitation_error_audit.csv` to fix the remaining imitation errors first.
