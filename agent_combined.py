"""V14 route, adapted to the 1.32.7 market.

  * premium-sale preemption widened from 1 step to 3
  * the 13 end-of-season wheat plantings the schedule lifts at age 3
    grown as CARROT instead -- nobody in a field of route clones grows
    carrots, so the town ends 400 units short of them
  * CARROT/TOMATO/EGG sold off the real price ladder while a unit still
    fetches 0.3 x base; the recording has no SELL order for any of
    the three, so this can only add sales, never retime the tuned ones

See kernels/build_combined.py for what was and was not combined, and why."""
import base64
import math
import copy
import json
import zlib
_ROUTE = json.loads(zlib.decompress(base64.b85decode('c-qxnO>Z075&SPY&%ylAhjY`~Ojd~2GGsYKVi1c3k|02k95%TH`R~zM<d8F6U0vPp(b}ArE0Z(t`*l}WSAY4>#b1B=`5%Az`QkTUE<WCV`gE}yF8=n@KmYu%=RZ7u{Kro}|NSrje*XOB;=9j({PE-C!~4(go-T%q?f0A8=l?F&yWz{l_jiw*i{QgAKfnEO_rvY|^RM4MY@dH?{`~3t&F169us;05r_JX5^Phj%+&_G{7%pdj-Z$a$_?q2+he?0#-u?db$CKBMJ^OO8-F$lb+OF}#yW4$B$Df@x=VffBBl2l;e}8PpTioguZuQb_>|tal&HeE3`1JkP)*V0Xr_27-Y4GfY`;MzG`R?=G{rexE|M%(hVVt5j%zq;H=l=HH<~aTf>1Br>fw_MErw>o#j7(oT&iZeEnI7p)`){5urrW2@qxazBx{4mW|0W!!LmytIc=Fu&2(m$%?QrzmV`p0C-uC7AT(IRzGj2LFKA4P_KF_ubpB_H%M;Z)L%RJi^dhE*K`AyS&(q1z(ou_#`SjSiPo@QmVTBcbVEPc9d2gcumF`9KHw~P*rJ1$iBPq`64Ihtof-?DmgBhzd392&g2tuGqVayvv_t^zhP_2*6v8fZm%%d9Zy=l;n{Q(wJd-l52T@^F8@dH3|=Z#R!mclURH`Z~kb5J;JG;b?$G2AV-0aJZ6E4fU3G!{{WNeK-nxPSF0Dsf85(rZQIf?b_un-=<;b_z8D=_fFo)yq|iUa}U=z$k#jlWN*5dyZ+Ym_T6qSa_;PC<iy8?^|qk93m)V&^=g-JyM*H`I2cBoqJD%QFa6wE44bAj#6Q=oO&LcaJZKN*O>Gpw5aL0ov}5ktNINEM;E7XNXwz|ED`PWtI!gTk)8&kK*g)oR7tXg97qH2@!~JhLq0@$K%N;faDi^aqe|mbn-F~-ueEj1t*yih9P$^$!pkpcDX;BNMZfY0f>_fK;a;TZ;2(RsbH@4oA2iN;#jpl5F#jfNc4FCeJyp7+x<n{?$eLM^C5H<Th0G<e+3H&g6TQ^-)Q3nimoE;%Bc?d5CPG7_F06Qr5DrrmIkVDnrJFbV=Lb1lgc(Bfb2B`z$_>dWPR<uKB$YBj9>;>BCmpc!VN{$-Yf@)N@dSA6h&}t7X-(bYAo*P(cH&A*@#TSW=-^9qV@Ul4*Y7d+_mA@>w+s8l1@e|}R+ky5%KwVsM5G<=a9Xv)4BY}f%?vmyjxIZ2FF8OuLl<vKrwl^^r$Dd)Z)<)kq^{d6da~qxD@xDvVnru6RiOWwVan3pohv!PR#tVg~HMlF8*PO}jaL|J_p@ntebJbmixjnMXSStm89oY`CL+1N<v8~qbF8L-&KXle{#(EhYHRhT%I>M<U)U?tt+7+Y@W9-UFgr0Z+tqpLz^v2ud<wI?a&mY$Vx^O)IPI2_y_2Wj1PY1BjvIqz&M}7nEx_*Nd5CGOj`60xhI8KG!(PieUR;Q+eS&%?Pz9|f`%EJ(f=?z}<O)l^HOr4tCSr8@>ua|)ihVM2250=afar7zWesR4kUyX_TmZ3@sCPOsD*u|{Gb*+t3GAaP1UkE*jn3B7eX~0oN^?MmF3A@8S2G4N#p!bgtADsy%w$yR6JUra*(^J49J?5u8Upnv2v26QbK>_q?>((trw{Dr+y}B{Uy}I!^<BHLrOuU8TV+~9-yWM9Gsksv%{Uou@*yW~7d*awEglsF;$jj1yz9z&ZwN(Dv(!E`mMMUB2V^_er91=kiZ#$Y+t_e2t7L!3%dY4<mJT@d%W*{giN%GTK;S}`V$Y*P0PlyK6z$}8)=&W?JlpRUHDRBB?5BDUlWS5c6b|GUjU@8El5yC4vxtiuT1UgSNMu>9GGy4;a30*|Vd0~Me5X6#~M+?EzhLm{VGbEnq7r31XuuP481D9rTqX0?|Sd7+svj%M=Z^Q)(1>=L+`06qshBJ#;hKF%^tJouKX363ChoN=B4b;+QfZ;MoWTfKdPhX4TC;dj-ZUfMSagDsc`yFmdtF1#aqun7MT2hrNw?Na|ln*AKwLGn<*CrAf(qQX#z~f%k{F@wVn~IbkS#(gpVvY*r>~G(-5j+*@Be)*fvU(~}<Nx&B9Y;*SMwhz|NtBU8lJPv0q$2EXSR+PX373i4)*TAhrb(0ilE)^PgK>d$PN0Rh;`mnY)@TmS+q-aXo-{(?C&4@1>r6tHLe&HosOvp;B~LhZ)NJJ{>jxOvz-T<aZya^wWyZ^dq3_m?ficqDRm)xoO_%7PtRz0z?M!hCBiB>RZgZJ;9vW~Q2Dol86};1F<XegpYodYcV$U3e;7F4&zmKnW74Z}MDuAuD@F7@8%I>FLtIW%!sPQtGG|E19MtdTHZdr?b@uoHG&_YRNPER&Rk(>2PY$|Z8zM7gyZurQ0u0;??T%4N5B^z0eo}*XW8Sj~^3GVyQOjZwac5Ytp3N{{UV~MjNu_7QnUQ2-MpNDFPz}oCOw%@iY#swLzgHq0-pBkHi`r}uNh(0wL+W0)+CBP0F&`zi$*v#e!W*1mxErAPU;vwa;$c2lyI55W1^oDMuJ2**^5rDzlKgpTJ`@{5yyZhe@HVwK&5cdgsD@~q=wNg$W%^a3;vP>!`=eWG1v#f<!teA1SNv<RxM?0ynb|IPW4*g>kpqnYp?c9dB(owJLNaqA|_ZC+r8q-vu`nnUkzjT7`x*uSJjv!dTzSKnIp2-DiZwMMo$tq3BUI6GaMgWL`Zv|&a{91pw*-O$GIIDx><c(dimWjnis(z5|FAMgFU9S1g)Tad&y#>Qg#F(}DV8JZi3j^}lcKxH(!@W0Z;Ol<ey6nfH#U<DTP@$a2->bN8Sxg5guhjMkNWMayr4u(BiHbz*;9;j`S!<I+xi<-?aX!f~nn5(G(Wu%UjA$xwM4a@MO`M>xH$-0WQYUJELpY;OwGcsE$f}t~96Ud=HT#M4XBsvm!uByIO`$q4KRZVMhv4hfJ4O8!M3enx?G8;Ik7NPU@gK*v4;+2krTIF)@|W@@*#TEQ7c@h1atoT8kJ+IrEmwR5@ij<|8?Z-bCm=n>EYP5w&0rDQv&K?3VMhXhO7r=XI&JF8W7ms43Egv;+N6b$7rOAlx)~1v;Lb-)CYS)I*P+BK#{)%QaBQ?}yCD4O;}`6iO@e#gk>rC%;Zh<-G@E3<4A}g14~SnHLEP^kE8L`jPRc?n6b~6XeK-^GR#}(lK*RjxHUSQ^23A%GV4Yw=qDEISqDE{BHHD#Dtu3j+R-s|!Z(it<yE#HNnCcAi`fe}|LMXM+y`Lx4UGO=$gkb#Dc!v~xNsM7LcaD&;sLUu_1cg|(n{1a}mOM&pVZAE5AoS!3VoNnWa_s3O3xUIAM0k?JoG1#ljBOi+5!g*baqbM_Z5wi8%I{OGn9)kdH78ZGNDNZ!I;A!WI4etOmTWY&I|5?u72*WtY)j|^W2b7=s-#9Q!*@x@f|ZD@@Jlq6vFrzP#?+KmnX^pGs_@noq)Pg_7v0z~I=%NB3`Bvg(joWp|H!?h4NnQ+Va_#(a3Os=(YqYKc6zxl-G5o=?&pmz_yJY>0GFBqpp=x^QdvjN)bxm$#g;Vj!r7g2W{(+lS|)L-1do=iKs<X1hr=4S<B!B32VC(|DiD}r>K12gJy}Q*dpMB1NjO{yIyO-#wnGHy$y(AUjmY<4Mo>`%Ns)s~e&K|qIKW1QKf=MI8$PpV?fOHdD10v#q+d|hOVhf;djR+vFu)8q4RgL<$lO=W6|TTG5hfcAsF!@{SO|eqfpzXU3<XX<HXE5^kcS1~7GZ3k6FT|nC80ZXsAO7$u8=iT1g1w){t5B<8P|jzhq-hEyN-<R3qV2jM33=l)7h--0gIt&HE%3C#T6;nwRTM7GHp{xyi%kxo?okrn`%Xu91Bf`bbrvTf7Nd5d19a~iNT3@ClDmn;_x{=81>Wnqn@%rDb5?|9ac)EA*VRh0*R3Y$a7FRBeB*Zn=1Qk>r&4<SC=57J}j*-Rl0Q9ukb+ZuMx~x3~Fg(N&+@$%QkaRD>5=c?lFm;XApcbWtPTY+@Ms|8V3(d5GZqRwT~g3>B>8KVz4es6q&F9|EkVA(v$TWOtZiA910lu-grw<(yMMtn})b>Ru8%%f&0Ww@$;c<QcGVU?_4f&L{N@$g&HKF!sr?QOXo13^2&lV6XAtgN7DX<v0%Th)AjD$A-$F^D)jJj;i_dOZr3GA+K<~cRs8TD3ry7@`KwT!LOANYQjDBa^jei2Y$G+|UEmJ@_wH?bq3=jCUoRBS%)5HMFfq=M{MXb@IVG@xh~J=wtrPYy+X5_{M8kvqVq12p$BZ?S*IzN!B&gEE!Y7ct9iR+5IuT;f>bbLoJ(_@7Ft7RkQB2tOAwX>a)+&>@(CHQFnjN8_19eLZY<?z$5^gfcxjkL%4cA}VJHz_6jXYmc+=5A!p%O9X3~PEj3v{_kt_}0Eiv2EHgCSbjpoYqfyIC72g4l%sU>9X9Fe=A4SP@xDR3!<UU%jJ6#*GKu*n(VG53Q0{rD3v6$jH-E3r0*7!)_+c<tR*ryJ;=u0(X;DrI>OxDUoE5at1jyvxl-&!C$3OGsiz|6t~J(dsjK4RJT|vc7b)`*1NK-t0E`M<<TnEpLBng(!v@{9dZ3<3I#x`D46@omay}Q#jYr!ZnQ{xYz`t|Is|TQD%V8i#IeLdPxFanGv!207$-C$t`ag|2H#+US0u<q1Btod62l^qB8ytGMyMuNt^LlZrI9L4s<K<Kis?X!!PoQPbo?+r9huR_<^@pV7}-J~Lr`4hn7d64H|pHxvM4v<Y^VrOOPQUNT4PM;q}u*_6T6~`0>pSE8f)kj61u1Y;x{>@lEAABNy3{e?-4GF9wD$mm#?6&oJq!OkWntg!dpUyeUxONm$-8OC6s4|zq-Vmf2vS8NF}4BI^ceqqJC&8nmc{shC(=#F!TgJ`WxstGY>Eu-J~i<T-t@BGjjAZp{19pzT$+H*lnvhTg==#r49oqIW8q4N?#=We5uYVaD1Ra$g&|-dRR*~JS*O;Wn-ea7Iqax*SnR%9jd1?4R*F?nN(e=91a38P%KBs<-GmM0_L)xv{Zs-VTH#bC|@qh#PcJn6}N!+CO%fUA5H1Y!lIE1>yRuk5F>;bvUj}Wr5R_LGU=qIKs1lFZiHi1TP6U_#X|_L6+M1Uc{Cyk0UD$?yG(!BW(@+}xU3R9dlVfPDc6a~0R?+F5Gux-z^m@r04LkxEON4Il%-9T>6CEyISPK;{vxLU^UoO3upvK<qYH?ZV!q_H*i}Xj_w8bR8o~7n50`4xS|W5C5l9PDPkfq}%u!)=k=kN0Wg#mx)jeJI8}q=E1-K^Q4`vYbXNb3C&B|2qVrFA9;_o^OA))!YbcllN*}!4QaK4J(7D!Mfe6VdTCM>A|3sN5h_GY<k^K&=>jVjAcPx7TwB~6(+V2Ti!K}y5by~oz2#|s%zA2U<ISe|n!ASSF<QB1m&WvUz+A{8l)i`fV!XcFoqp2q}ly=|13DNQnPRdpA2e`qZWG<z5WiP@x+(8F4Az`!fRsRK6!?3ZdhD?=FU$?Zm<hOiM#KxD3J+>k*zgMmu$Kq5jH(>OZu=4uYHtV9XCEPdxq&nJPu9Nx_e_QuAm0Nw+ei}4GsdoUeWWxlLGb`mqSN=-5Z58@DAvd2Tto0kkcP=J6m>UvkH>O48UZeEjp-ic-K%4)!@ZnGf*R1|C>dA5aTwCzOamZW>+qqW?s4#GZQ=-5fhwJ7^Ew&tmTj>uZUA(-B!N{p7E7omhXvEEz&Ox4lGJaFdA@+zNa)YPV+YM8y-S4>N1_DB3}VAaOOfzPoS8Cc<)8(~bVB4@VVm6$H!hQo_Jj$;+%2NxLz8>c+eWQfL+E{qzzl_ZU~Ay=ELJ@wMr*fNGeO4c~T1*x!CB*ikuNMw`WAeA7cfKX9umFC2Qs8jHGUBf0qL;z!Df%!@5fK~<*!T^$Pq!-#Hj@HetR`S*X6@5|v^w1R`WGx!X)UxdXW{cY+f{cmBD>LBXx{Qz^Re++|2U5YLTKog5dfNiJ%__u`75w(~RmD=(mU`zMw8xcwO|Mc~0Xvv{GQN{5pht*%)wfj;j#TD)I@(<kh2Ez5l~Oai<^@DKzf8#|xJQ`GXfEMYijwOJR%ql8H72Pu&$EZ?{sl~J#JK=^Is-{JMn2zR0F?Pis+-Z|fvE1PHxOR;&ZUaRBk&|0Uo4SYOGph}r0MYKQA%G8D^N8FXMswHF@uiCGz)}pd`3AMy0fYpZ+EGxp|<IIr4lW-%B_vtNq8@+m8Rv*&@3d9AH*lc<UztD*2Xfg>^2V+K%`7EQfJ1?jk69&<q`yEF*&=mI(iu)YN191<^{qkOcd>OV!&F4MNDH>T*P=u=vE6&qzGs;H6tqs=M_0jz{d3kr*Oy9Ng#+Vyg~5p7K?Ou+z~1nR@&Sy!%@Y7>&u>@Vv!x_WF&xtx<V0(9J9hUWx9ZF5rTfg6OB0p7BzW+isEzeYF8<|HKB>TF+zS<X&?p=n*)%hRQI5onb4?VvA+8CsoQfv>9QzHQ43YedV+b%N?hKxxSfw`MnbVvesSe>)g>_?hX<zn)x@bI`CW3rkaxCb1Uct@BEu|<Vg{ZoyTT=LKs=Y5`-cypHtkm7eg%e6nl7W+D^0=`Bn#DUDkyPA_1wjnbZROjQ46W48q0omTqDQk?7_(@g3^fX(yI9a{&eKcnn43AfLKNQX<aN6wY)`<9j!VXi?z>=n1m=)0!9*UNbd%N6iHHv86U|kt-{-NT9pT@Xa~YpqRY+>7NG~WSUl@OKoVeldr`d7aqHVMNeD{VR62B=$8eo-7Os<I5U#d}ZLKXA$!4O$jM@A*uRrsaa5|L-rSiPMAjlX?Yn7IwNd1FfWA@FoY1pz#tvG>h0|Ye5We1rfHUtm|yl~$uBNfdAQDNj-6(DA}uVZQ3%%E*PiWgjpL|H_{f`LlOJfNfGNU{2=mXl>kMtc00Cx2!NalSpplJ*zo<u1`NuBKx9A0}o^rq<7`BMLC~6b6ba5I0&jgL8`;Fre#BJgHjgQN~xS18y-;FQ$IId)OYzmLP%i^VJersztV(*s5Zxz~*zPsTWbJ5BCO`?NNFQ|7OhGY8A4Gij+{{KGHlA$DJ!EcNV&U{eXujmte(T_{x#^c4bWj5zUx)FRR1DUCGUtL{1ccP_5F3l*bvocq7TRGH}0B?e4&@W<5KpTDB+gFeBV0_?&5L21Ou(xGlGFs{A)8nKQ`yCA3J(0mVxxI!~;D|J~=i`}aRS+b2(-A7kx5o~A=OfD+5)g9O;X&p&>*nOHC>nIG#CfR-Kxy_B=He*-#7$UO&xp#dIAMqObAg9-$>LUoJCDBu~L=wCU=(xs*^LAnE<H`3e|OZ7-#56N_fP+=5)0HDWVl}~LI!@17LXuh#dpP;@6r(Y-^r5@;Uk*j2l$9<`wbvfvaSJgO~Vwz+`PwFaB5XAJinyE}wiHSUMoOa9+v8}392udOyuqm&4S*o2@|3=TE;P4aSdXaG8OmA#}yL#P>&#c~jyHc;`<VBsMK+mdwW?c#kC{ma>oD$Q~edwi_<3nUfL^!3QHL>WxJ7Ps|A|_EnJ4L1u>9t68nOdK{AD&A$J3aG`hPgu@yiKuV2-ygBKXJpC>F7uxNNp=2K{*p)3+fY)6rk#cK_jFq4=cqg8bp5NEI2ReBT<ttS$?wwEM_Ylc;<SpAxaIipd3g=>yZ|=AbD6p14ucV+^|SXNzbxk^T^6une$D_Xj3JhSaKTy3K$Oa^$3bYpAuL!Ey|N@oJ2{%*A&r07M;Z0R$$iwzZZyGRVihZDpx8OAp@B(xgj&_jH#-S8ra0s3~f8IoJ6e^<d8B6naWC1bWmA43Z+l1*l=DTcKw>pYje4gN`jIj`P9p?y{tO6@M%|S3D%gseAY@P%#b2~(H!Nh))BIBf{G_zNSpGg`H=it3Z<xJ;3BSAQ*9MAX!<oqU2XI=6Ff{*)VbVM!sih2P)u9ZhGdM^gts^6sSXXHc<ilE@fqgqI{`s8bbaPzm?%XI$LEt$G<La)p=F7B*r$M|Q(G@`Ad*#FV;c;F&xwn@C7f1~KO`zMY&YEtP<qa=&bX$@B_iBaQFILhw(#U|5?Uw>!KH~r&6|wUf@Kqld=kcfXR2t)?JtBqodqVB4GnNBYDSR^nnWEkv}<$`<1I+Cs3Zc@V>CJ&COW7$6+#Eo{o@u2;zQWSk^`W8w50%KhTcmlKh#kvo(=wPq7dLo9-~v5HdsT!!c$VwjqYe|5<xDGfHVg67OkAHU9N7`sGPar?D~-$YA`E>Knj}8?2CDVc@@bg#tg_|m&rx8GvFWR-^u}>im0>2hd?uk#<FdyTJ$_F=yf&`V+BehC4Aembef7T`RLfHScHkDH7fZk#hObQ{)Z?A(}KoDScjr$6LqP3&Wu)RDWy%)A5_D3YZP)pu9&EgQ)JyU+a|hjWhGsAvt=w-US^5grJP62eR7d`v)bvTWUhbfo(HU%S+PjD&=Qn|m~+L5mKbrFTk)r8YXUoq31+~vS8;(@NbODRfO(oOv1FkP(lE_QF`M)<L(rmchKpW}Ds&=ip-*--hnk}4U8nN5d@MA~;ew{MPwG!@!j)3^B|=P&$rQX`8^_>$_12;S!d6J?Piq6wdR&vUV(n;QuQN*0o)T}3Du;ITT%}1-15MNmb~$Mo`A4Ei)mot~kn&|>dLcx~2xN8?t=NJcsKZVhC(V8kw6vuLzRd`OixL_n)DJj8Uh-{>S-t61ElO!HO~7Wh#4<<EsgPNwNM6UP&1aU=ZOkiKdr+>zwpm4ll_q2%Su|NB(@=V+-Z&|kA5dk)*10C^83-{f+XVJOwqBFPwibzW4n*To8UGZiV#Zf<LR5n1B9b5MHPEXvlFzdbIMQ1^zEX&|Tsms$9Xx1FmtKsJixQ_Yl70>PEk~cy`CS4Hi|~|aCGUjvTs9$v7FyYeQRWPb1{h9c1BDQW64j3lz>GA~Lc$$`0_lEnr2xx615Ja_-Q`+Vn)}OqpEeE#M{Psok`Fo)1DC}dR`Cf#VW=o6pQ#T~qGK_H&B>$Stjp%b={3Tx>imx_Meo3wSQ55P@6a%L0G>I4f)}IMlOvMrGUpal!%@SSE$m#UggBDb=v18>+zAs)KM~vj>=3=sDXSvJ6j&+V7>f#{d?-bhByTv1QzR%M*XkvuG%?apA_LCKf*&CsNb;f1mLb)S!*tX4ScOav%5>Cjr?+ujOeS?CYZS5PhV5SOI_rgK13hv-Hw96t^U8;aY*%(0>77~aUQcmEnkbSpRHT|{jCGoy9f?{tqEf`D;-TX(P)s4Hf(jgMm&Ga_S$f~OCVbQ^X+tdVdtPZ1FZo18tQaWu!dFtt(C8GKNaAEG%%Orq6`>}MVriNg0cKiiU|0i&m*1m@AKK0(FoVvEy_RO`K+y@~Er>>v5<R?g_Ye0tw+i<(K?maEjG!}IjMUgKtlm-u&W-BJI0C+@igAf^D3SMDOZuP=d_)kUg(WFcRtRkpP%}u0U>wS-l8Vy4aK?G&7L(4OCbiVssX?%QJP(XIDME_U7E0xhVX_F|M@fAVbYr-5OVX!fZcnByS+$jlu*{)a?cj$!UrQY|iJE}sUw6xvkpvF|#*6#Cl@F}w2_9;845`YNR7nYdkjaJ@q$fo#O(_sXGn^a9EvhC<K*tWGIO28!8%LGL=0+LI11hdbvF<Uh-CcxZTJZ~}E4kGx#whdAgW?`(u~0`t#D63mOOl7d`DZHYhq#!zpsZSin--S_yQO8-Ve=M;iDVeEievUzmsDCRlSva~$PoxB=ZEuDN17N%2?%P!n*w;ntE5rVpNe?qE~Txi!A_$CaMPy_02{{JD#E=00kBE#iXuwLI%hRW0%IcF$x(tVs6@&kbz4J}qR@8m1CXCZ=s}8tEeezpR<zAy-lkITf_dKCFjBF|B&CE|Yy?-a)!IcF93vJmJ#mFli){=^cCb<rWD*4BV}CT2)(})#YK_T3+BMJ|)>nNT`7Q#nZDfb4X+a~eK~Xc;LtnT*ZekM$J{q>V6(6pLjmEr{gcDA=mc{zzTS2QKtM55K@&qDV*y5=E8m>&s>>_Hw)yk=JN_!%EM`IthPB}|WMwY7okGY6qpb`-o%u>!zZfsJ;&(N+Yxq?(qL`-r-Au8#hD?luIppeM+De6E$JLb+}Gr<SBn)AGIoE5`Q?;LI-SI^wYr0>i|jczki@?_x03&5fZRNBi-T0UiW@C1A@c3Vu$_k-5n%o1IJILlqovmT91%Qd2>FA&O9q!tb-1cO!(%(@heT23RKu(m3x!_geGq@ZUYhT>PxN%>!m402b0C{KJ>=-%XmQayu&%=g>jDzUr@uNGSs+)=Cpm#fa<<<MKql~fLm24|=7HmL9?yM$~zT&<^^HOmoS(h#9EayB4HEk4x*Q`A&athGRcCZqVPTzwNUpQXEBia~!mP<-Zt>djLe`(~HPrEU`AQ_D<Nniw(65~Oq*O|5cT`3|6bOSY`*>=H#<Q4BRF8kNHf&@1!`tjNGlH7#a-#M>ag4vIh|%MocU0Gb>*CcGA>pT<Z_3Uz_YK0@`Pk)yw%KTa(;wBDHlKl_#rq5z11nhcamYy)qZNQz~dij7k>Z9_C_=49seZE1r+oR&z?fp5=$$FEHz1hZ7emo(()!<&BsESow1n8whSLh<YU%cyThLXAYi{v_TMI(Ms#cUP#!NNQ_VM31gB@_4)d?*0c(Djk>')).decode('utf-8'))
_EARLY_SALE_ITEMS = ('MELON', 'MILK', 'STRAWBERRY', 'WOOL')
_EARLY_SALE_STATE = {0: {'last_step': -1, 'due_step': -1, 'due': {}}, 1: {'last_step': -1, 'due_step': -1, 'due': {}}}
_ROUTE_FIX_STATE = {0: {}, 1: {}}
_ROUTE_FIX_TAIL = 8
_SHOP_DEMAND = {'BAKERY': ('EGG', 'WHEAT'), 'PIZZA_SHOP': ('MILK', 'TOMATO', 'WHEAT'), 'BRUNCH_SPOT': ('EGG', 'WHEAT', 'STRAWBERRY'), 'YARN_STORE': ('WOOL',), 'ICE_CREAM_SHOP': ('STRAWBERRY', 'MILK', 'WHEAT'), 'PET_CAFE': ('CARROT',), 'SMOOTHIE_SHOP': ('STRAWBERRY', 'MILK'), 'FARMERS_MARKET': ('WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY')}

def _value(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, 'get', None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)

def _copy_plan(action):
    action = copy.deepcopy(action or {})
    return {'farmer': list(action.get('farmer') or ['PASS']), 'hands': [list(order or ['PASS']) for order in action.get('hands') or []], 'market': [list(order) for order in action.get('market') or []]}

def _player(obs):
    return 1 if int(_value(obs, 'player', 0) or 0) == 1 else 0

def _farm_view(obs, seat):
    farms = list(_value(obs, 'farms', []) or [])
    return farms[seat] if seat < len(farms) else {}

def _match_hands(action, obs):
    action = _copy_plan(action)
    expected = len(_value(_farm_view(obs, _player(obs)), 'hands', []) or [])
    hands = list(action.get('hands') or [])
    if len(hands) < expected:
        hands.extend([['PASS'] for _ in range(expected - len(hands))])
    action['hands'] = [list(order or ['PASS']) for order in hands[:expected]]
    return action

def _tile(farm, position):
    try:
        x, y = (int(position[0]), int(position[1]))
        return (_value(farm, 'tiles', []) or [])[y][x]
    except (IndexError, TypeError, ValueError):
        return 'LOCKED'

def _scheduled_unit(step, actor):
    trace = _ROUTE[min(max(int(step), 0), len(_ROUTE) - 1)] or {}
    if actor == 'farmer':
        return list(trace.get('farmer') or ['PASS'])
    hands = trace.get('hands', []) or []
    return list(hands[actor] if actor < len(hands) else ['PASS'])

def _repair_weed_block(obs, action, step):
    action = _match_hands(action, obs)
    seat = _player(obs)
    game = _ROUTE_FIX_STATE[seat]
    if step == 0 or step < int(game.get('last_step', -1)):
        game = {'last_step': step, 'active': {}}
        _ROUTE_FIX_STATE[seat] = game
    game['last_step'] = step
    farm = _farm_view(obs, seat)
    positions = [_value(farm, 'farmer'), *list(_value(farm, 'hands', []) or [])]
    unit_actions = [action.get('farmer', ['PASS']), *list(action.get('hands') or [])]
    active = game.setdefault('active', {})
    for actor, transaction in list(active.items()):
        index = 0 if actor == 'farmer' else int(actor) + 1
        if index >= len(unit_actions):
            active.pop(actor, None)
            continue
        age = step - int(transaction['start'])
        if age == 1:
            unit_actions[index] = list(transaction['intended'])
        elif 2 <= age <= 1 + _ROUTE_FIX_TAIL:
            unit_actions[index] = _scheduled_unit(step - 1, actor)
        else:
            active.pop(actor, None)
    for index, (position, intended) in enumerate(zip(positions, unit_actions)):
        actor = 'farmer' if index == 0 else index - 1
        if actor in active or not isinstance(intended, list) or (not intended):
            continue
        if intended[0] not in ('BUILD_PASTURE', 'PLANT'):
            continue
        tile = _tile(farm, position)
        if not isinstance(tile, dict) or tile.get('kind') != 'WEED':
            continue
        active[actor] = {'start': step, 'intended': list(intended)}
        unit_actions[index] = ['DIG']
    action['farmer'] = unit_actions[0] if unit_actions else ['PASS']
    action['hands'] = unit_actions[1:]
    return _match_hands(action, obs)

def _lead_state(obs, step):
    seat = _player(obs)
    state = _EARLY_SALE_STATE[seat]
    if step == 0 or step < int(state.get('last_step', -1)):
        state = {'last_step': step, 'due_step': -1, 'due': {}}
        _EARLY_SALE_STATE[seat] = state
    state['last_step'] = step
    if 0 <= int(state.get('due_step', -1)) < step:
        state['due_step'], state['due'] = (-1, {})
    return state

def _town_demand(obs, item, step):
    demand = 1 if item != 'FERTILIZER' and step % 24 == 0 else 0
    if step % 4 != 0:
        return demand
    town = _value(obs, 'town', {}) or {}
    for shop in list(_value(town, 'unlocked_shops', []) or []):
        products = _SHOP_DEMAND.get(shop, ())
        if item in products:
            demand += 2 if len(products) == 1 else 1
    return demand

# How many steps ahead of the recorded schedule to pull a premium sale.
# Stock V14 uses 1, so two clones preempt each other identically and tie to the
# dollar. Measured against stock over two independent seed sets, 2 to 4 wins 31
# of 32 games; 8 gives most of it back. See build_combined.py.
LOOKAHEAD = 3


def _next_sale_qty(step, item):
    total = 0
    for ahead in range(1, LOOKAHEAD + 1):
        future = step + ahead
        if not 0 <= future < len(_ROUTE):
            break
        total += sum((max(0, int(order[2])) for order in _ROUTE[future].get('market') or []
                      if len(order) >= 3 and order[0] == 'SELL' and (order[1] == item)))
    return total

def _pickup_holdback(action, item):
    reserve = 0
    for order in [action.get('farmer', ['PASS']), *list(action.get('hands') or [])]:
        if isinstance(order, (list, tuple)) and len(order) >= 2 and (order[0] == 'PICKUP') and (order[1] == item):
            try:
                reserve += max(0, int(order[2])) if len(order) >= 3 else 1
            except (TypeError, ValueError):
                reserve += 1
    return reserve

def _market_sell_qty(action, item):
    return sum((max(0, int(order[2])) for order in action.get('market') or [] if len(order) >= 3 and order[0] == 'SELL' and (order[1] == item)))

def _remove_advanced_qty(action, state, step):
    if int(state.get('due_step', -1)) != step:
        return action
    due = {str(item): max(0, int(quantity)) for item, quantity in dict(state.get('due', {})).items()}
    action = _copy_plan(action)
    market = []
    for raw in action.get('market') or []:
        order = list(raw)
        if len(order) >= 3 and order[0] == 'SELL' and (order[1] in due) and (due[order[1]] > 0):
            requested = max(0, int(order[2]))
            reduction = min(requested, due[order[1]])
            requested -= reduction
            due[order[1]] -= reduction
            if requested <= 0:
                continue
            order[2] = requested
        market.append(order)
    action['market'] = market[:10]
    state['due_step'], state['due'] = (-1, {})
    return action

def _advance_sale(action, obs, state, step):
    if not _EARLY_SALE_ITEMS:
        return action
    private = _value(obs, 'private', {}) or {}
    shed = _value(private, 'shed', {}) or {}
    moved = {}
    action = _copy_plan(action)
    for item in _EARLY_SALE_ITEMS:
        target = _next_sale_qty(step, item)
        if target <= 0 or _town_demand(obs, item, step) > 0:
            continue
        stock = max(0, int(_value(shed, item, 0) or 0))
        reserve = _pickup_holdback(action, item) + _market_sell_qty(action, item)
        quantity = min(target, max(0, stock - reserve))
        if quantity <= 0:
            continue
        market = [list(order) for order in action.get('market') or []]
        existing = next((order for order in market if len(order) >= 3 and order[0] == 'SELL' and (order[1] == item)), None)
        if existing is not None:
            existing[2] = max(0, int(existing[2])) + quantity
        elif len(market) < 10:
            market.append(['SELL', item, quantity])
        else:
            continue
        action['market'] = market[:10]
        moved[item] = moved.get(item, 0) + quantity
    if moved:
        state['due_step'] = step + 1
        state['due'] = moved
    return action


_FINAL_SELLABLE = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)


def _final_drop_cash(obs, action, step):
    if step != len(_ROUTE) - 2:
        return action

    private = _value(obs, "private", {}) or {}
    inventories = list(_value(private, "inventories", []) or [])
    shed = dict(_value(private, "shed", {}) or {})

    farm = _farm_view(obs, _player(obs))
    tiles = _value(farm, "tiles", []) or []
    size = len(tiles) or 10
    half = size // 2
    shed_tiles = {
        (half - 1, half - 1),
        (half, half - 1),
        (half - 1, half),
        (half, half),
    }

    positions = [
        _value(farm, "farmer", [0, 0]),
        *list(_value(farm, "hands", []) or []),
    ]
    unit_orders = [
        action.get("farmer", ["PASS"]),
        *list(action.get("hands") or []),
    ]

    room = max(0, 100 - sum(max(0, int(v or 0)) for v in shed.values()))
    deposited = {}

    for idx, (pos, order) in enumerate(zip(positions, unit_orders)):
        if room <= 0:
            break
        if not isinstance(order, list) or not order or order[0] != "DROP":
            continue

        try:
            current = (int(pos[0]), int(pos[1]))
        except (TypeError, ValueError, IndexError):
            continue
        if current not in shed_tiles:
            continue

        inv = inventories[idx] if idx < len(inventories) else {}
        for item, raw_qty in list((inv or {}).items()):
            qty = max(0, int(raw_qty or 0))
            take = min(qty, room)
            room -= take

            if take > 0 and item in _FINAL_SELLABLE:
                deposited[item] = deposited.get(item, 0) + take

            if room <= 0:
                break

    if not deposited:
        return action

    result = _copy_plan(action)
    market = [list(order) for order in (result.get("market") or [])]

    for item, qty in deposited.items():
        existing = next(
            (
                order
                for order in market
                if len(order) >= 3
                and order[0] == "SELL"
                and order[1] == item
            ),
            None,
        )

        if existing is not None:
            existing[2] = max(0, int(existing[2])) + qty
        elif len(market) < 10:
            market.append(["SELL", item, qty])

    result["market"] = market[:10]
    return result


# ----------------------------------------------------------------------------
# Market model, transcribed from kaggle_environments/envs/kaggriculture at
# 1.32.7. The agent is handed market.inventory and market.prices in full, so it
# can price a sale exactly instead of guessing. Prices are recomputed per unit
# inside the order, which is the whole reason sale sizing matters.
# ----------------------------------------------------------------------------
_MKT_I0 = 10000
_MKT_PRICE_FLOOR = 1
_MKT_HINGE_GAIN = 8.0

# item: (base, T, below_func, below_target, above_func, above_target)
_MKT_PARAMS = {
    'WHEAT':      (25, 400, 'sqrt', 0.80, 'log', 0.20),
    'CARROT':     (35, 450, 'hinge', 1.00, 'sqrt', 0.70),
    'TOMATO':     (60, 200, 'hinge', 0.40, 'sqrt', 0.60),
    'STRAWBERRY': (120, 100, 'sqrt', 0.70, 'linear', 1.60),
    'MELON':      (250, 300, 'log', 0.20, 'sq', 3.60),
    'EGG':        (50, 332, 'hinge', 0.40, 'log', 0.20),
    'MILK':       (160, 122, 'sqrt', 0.60, 'linear', 1.60),
    'WOOL':       (200, 105, 'log', 0.20, 'sq', 3.20),
    'FERTILIZER': (100, 200, 'linear', 0.40, 'linear', 0.40),
}


def _mkt_shape(func, x, T=None):
    x = max(0.0, x)
    if func == 'linear':
        return x
    if func == 'sq':
        return x * x
    if func == 'sqrt':
        return math.sqrt(x)
    if func == 'log':
        return math.log(1.0 + x)
    if func == 'hinge':
        if not T or T <= 0:
            return x
        u = x / T
        return u + _MKT_HINGE_GAIN * max(0.0, u - 1.0) ** 2
    return x


def _mkt_price(item, inventory):
    p = _MKT_PARAMS.get(item)
    if p is None:
        return _MKT_PRICE_FLOOR
    base, T, below_f, below_t, above_f, above_t = p
    if inventory < _MKT_I0:
        amp = below_t * base / _mkt_shape(below_f, T, T)
        price = base + amp * _mkt_shape(below_f, _MKT_I0 - inventory, T)
    else:
        amp = above_t * base / _mkt_shape(above_f, T, T)
        price = base - amp * _mkt_shape(above_f, inventory - _MKT_I0, T)
    return max(_MKT_PRICE_FLOOR, int(round(price)))


# Exactly the products the recording has no SELL order for anywhere in its 720
# steps. That restriction is the whole safety argument: this layer can only add
# sales the schedule was never going to make, so it cannot disturb the tuned
# timing of the ones it does make. Applying it to the route's own products
# instead costs money monotonically -- measured against stock, floor 0.90 loses
# $1,456 and floor 0.0 loses $3,761, with the opponent's score unmoved, so it
# is pure self-harm. Without this layer a swapped herd's eggs would sit in the
# shed until the buzzer and score nothing.
EAGER_SELL_ITEMS = ('EGG', 'CARROT', 'TOMATO')

# Sell that stock while a unit still fetches this fraction of base. None
# disables the layer exactly and is the A/B control.
EAGER_FLOOR_FRAC = 0.3


def _affordable_units(item, inventory, want, floor_frac):
    """How many of `want` units still clear the floor, walking the ladder down."""
    p = _MKT_PARAMS.get(item)
    if p is None:
        return want
    floor = p[0] * floor_frac
    sold = 0
    inv = inventory
    while sold < want:
        price = _mkt_price(item, inv)
        if price < floor:
            break
        sold += 1
        # The environment only counts a sale into supply when it clears $1.
        if price > _MKT_PRICE_FLOOR:
            inv += 1
    return sold


def _eager_sell(action, obs, step):
    """Sell pure-output stock ahead of the recorded schedule while it pays."""
    if EAGER_FLOOR_FRAC is None:
        return action

    market_view = _value(obs, 'market', {}) or {}
    inventory = _value(market_view, 'inventory', {}) or {}
    private = _value(obs, 'private', {}) or {}
    shed = _value(private, 'shed', {}) or {}

    action = _copy_plan(action)
    market = [list(order) for order in action.get('market') or []]

    for item in EAGER_SELL_ITEMS:
        already = _market_sell_qty(action, item)
        spare = (max(0, int(_value(shed, item, 0) or 0))
                 - _pickup_holdback(action, item) - already)
        if spare <= 0:
            continue
        # Our own scheduled units go down the ladder first, so price the extra
        # ones from where that order leaves the market.
        inv = int(_value(inventory, item, _MKT_I0) or _MKT_I0) + already
        extra = _affordable_units(item, inv, spare, EAGER_FLOOR_FRAC)
        if extra <= 0:
            continue
        existing = next((o for o in market
                         if len(o) >= 3 and o[0] == 'SELL' and o[1] == item), None)
        if existing is not None:
            existing[2] = max(0, int(existing[2])) + extra
        elif len(market) < 10:
            market.append(['SELL', item, extra])

    action['market'] = market[:10]
    return action


# ----------------------------------------------------------------------------
# Herd swap: rewrite the recording itself, once, at import.
#
# The route's animal program is 8 cows and 4 sheep, which is up to 176 milk and
# 64 wool aimed at purses worth $6,181 and $7,928. Eggs have a log price curve
# with a 0.20 target -- so shallow it is effectively flat -- and the town eats
# them all season with nobody restocking. This retargets the same choreography.
#
# All-or-nothing by design: PLACE only succeeds when the worker is standing on
# a structure matching the animal, so converting some pastures to coops while
# still placing cows would silently drop those animals on the floor. The
# rewrite therefore refuses unless every animal the route places is covered.
#
# {} disables it exactly and is the A/B control.
# ----------------------------------------------------------------------------
HERD_SWAP = {}

_ANIMAL_STRUCTURE = {'COW': 'PASTURE', 'SHEEP': 'PASTURE', 'GOOSE': 'COOP'}
_BUILD_OP = {'PASTURE': 'BUILD_PASTURE', 'COOP': 'BUILD_COOP'}
_ANIMAL_ORDER_OPS = ('PLACE', 'PICKUP', 'DROP')

# The recording as published, kept so the swap can be re-derived rather than
# accumulated. Rewriting _ROUTE in place would make HERD_SWAP a one-shot import
# side effect, and a sweep that sets it between games would read the previous
# game's herd.
_ROUTE_STOCK = copy.deepcopy(_ROUTE)
_EDITS_APPLIED = None


# ----------------------------------------------------------------------------
# Carrot swap: the one substitution the schedule can absorb.
#
# The route is 95% busy and acts on every unlocked tile, so there is no slack to
# grow anything extra in. Substitution is the only lever, and it is tightly
# constrained: WHEAT waters at ages 2-4 and its tile survives to age 5, CARROT
# waters at ages 2-3 and its tile starts decaying at age 4. Of 141 wheat
# plantings, 128 are lifted at age 4 -- a carrot there would already be rotting.
# The other 13 are the end-of-season batch, planted day 26 and lifted day 29,
# and those fit a carrot exactly.
#
# It is worth doing because nobody in a field of route clones grows carrots, so
# the town eats them all season with no restocking: a route-vs-route game ends
# with carrot 408 units short at $65 while wheat sits at $42. Selling carrot
# instead of wheat also stops us competing with ourselves in the wheat market.
# () disables it exactly and is the A/B control.
# ----------------------------------------------------------------------------
CARROT_SWAP = ((629, 9), (633, 7), (633, 10), (633, 11), (634, 9), (635, 6), (638, 10), (639, 5), (639, 9), (641, 0), (641, 6), (645, 5), (645, 10))
CARROT_SEED_STEP = 600


def _swap_carrot():
    if not CARROT_SWAP:
        return
    planted = 0
    for step, hand in CARROT_SWAP:
        if not 0 <= step < len(_ROUTE):
            continue
        hands = _ROUTE[step].get('hands') or []
        if not 0 <= hand < len(hands):
            continue
        unit = hands[hand]
        if unit and len(unit) >= 2 and unit[0] == 'PLANT' and unit[1] == 'WHEAT':
            unit[1] = 'CARROT'
            planted += 1
    if planted and 0 <= CARROT_SEED_STEP < len(_ROUTE):
        market = _ROUTE[CARROT_SEED_STEP].setdefault('market', [])
        if len(market) < 10:
            market.append(['BUY_SEED', 'CARROT', planted])


def _swap_melon_seed():
    """Pay for the patch out of the day-0 herd, in the recording itself."""
    if not MELON_PATCH or not MELON_PATCH_SHEEP_CUT:
        return
    cut = MELON_PATCH_SHEEP_CUT
    for trace in _ROUTE[:24]:
        for order in trace.get('market') or []:
            if (len(order) >= 3 and order[0] == 'BUY_ANIMAL'
                    and order[1] == 'SHEEP' and cut > 0):
                take = min(cut, max(0, int(order[2]) - 1))
                order[2] = int(order[2]) - take
                cut -= take
    # Melon seed is $80; a sheep is $500. Buy the patch and leave the change,
    # because day 0 is already spending to the last dollar.
    for trace in _ROUTE[:24]:
        for order in trace.get('market') or []:
            if len(order) >= 3 and order[0] == 'BUY_SEED' and order[1] == 'MELON':
                order[2] = int(order[2]) + len(MELON_PATCH)
                return


def _apply_route_edits():
    """Rebuild _ROUTE from the published recording under the current edits."""
    global _ROUTE, _EDITS_APPLIED
    key = (tuple(sorted(HERD_SWAP.items())), tuple(CARROT_SWAP), CARROT_SEED_STEP,
           tuple(MELON_PATCH), MELON_PATCH_SHEEP_CUT)
    if _EDITS_APPLIED == key:
        return
    _EDITS_APPLIED = key
    _ROUTE = copy.deepcopy(_ROUTE_STOCK)
    _swap_carrot()
    _swap_melon_seed()
    _swap_herd()


def _swap_herd():
    if not HERD_SWAP:
        return

    placed = set()
    for trace in _ROUTE:
        for unit in [trace.get('farmer')] + list(trace.get('hands') or []):
            if unit and len(unit) >= 2 and unit[0] == 'PLACE' and unit[1] in _ANIMAL_STRUCTURE:
                placed.add(unit[1])
        for order in trace.get('market') or []:
            if order and order[0] == 'BUY_ANIMAL' and len(order) >= 2:
                placed.add(order[1])
    # A partial swap would strand animals: PLACE only succeeds on a structure
    # matching the animal, so a cow placed on a converted coop is money burnt.
    if not placed or not placed.issubset(HERD_SWAP):
        return
    targets = {_ANIMAL_STRUCTURE[HERD_SWAP[a]] for a in placed}
    if len(targets) != 1:
        return
    build_op = _BUILD_OP[next(iter(targets))]
    old_builds = {op for op in _BUILD_OP.values() if op != build_op}

    for trace in _ROUTE:
        for unit in [trace.get('farmer')] + list(trace.get('hands') or []):
            if not unit:
                continue
            if unit[0] in old_builds:
                unit[0] = build_op
            elif (unit[0] in _ANIMAL_ORDER_OPS and len(unit) >= 2
                  and unit[1] in HERD_SWAP):
                unit[1] = HERD_SWAP[unit[1]]
        for order in trace.get('market') or []:
            if order and order[0] == 'BUY_ANIMAL' and len(order) >= 2 and order[1] in HERD_SWAP:
                order[1] = HERD_SWAP[order[1]]


# ----------------------------------------------------------------------------
# Early melon patch, worked by a hand the route does not know exists.
#
# Melon is the steepest curve on the board (sq, target 3.60: $250 at the top,
# dead at 158 units), so the day-10 harvest is the single richest moment in the
# game and it goes to whoever brings the most fruit. Across 15 losses to 15
# different opponents the melon gap is +13,584 -- the same number every time,
# because they plant 12 on day 0 and we plant 5.
#
# The insertion point is hiring. Hands are cleared and re-hired nightly at
# fib(hires_today), so one MORE hand than the recording expects costs $8 on day
# 0 and $1-$21 a day through day 9. The route addresses its hands by index and
# _match_hands pads the rest with PASS, so that extra slot is ours outright --
# no desynchronisation risk, unlike stealing an idle turn from a hand the route
# is going to move next turn.
#
# What it cannot do is conjure ground. NW is full, so the patch displaces three
# strawberries, and strawberry is our best market at roughly $244 a unit. That
# makes this a genuine trade rather than free money, which is why it is a
# measured switch and not a rewrite.
# ----------------------------------------------------------------------------
MELON_PATCH = ()
MELON_PATCH_PLANT_DAY = 1
MELON_PATCH_HARVEST_DAY = 11
MELON_PATCH_SHEEP_CUT = 1


def _shed_tiles(farm):
    size = len(_value(farm, 'tiles', []) or []) or 10
    half = size // 2
    return ((half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half))


def _step_toward(pos, target):
    x, y = int(pos[0]), int(pos[1])
    tx, ty = int(target[0]), int(target[1])
    if x < tx:
        return ['EAST']
    if x > tx:
        return ['WEST']
    if y < ty:
        return ['SOUTH']
    if y > ty:
        return ['NORTH']
    return None


def _patch_job(farm, private, idx, pos, day):
    """One order for a spare hand: plant, water, harvest, or carry to the shed."""
    inventories = list(_value(private, 'inventories', []) or [])
    inv = inventories[idx] if idx < len(inventories) else {}
    carrying = int(_value(inv, 'MELON', 0) or 0)
    if carrying > 0:
        sheds = _shed_tiles(farm)
        if tuple(pos) in sheds:
            return ['DROP']
        return _step_toward(pos, sheds[0])

    seeds = _value(private, 'seeds', {}) or {}
    have_seed = int(_value(seeds, 'MELON', 0) or 0)

    for tile_xy in MELON_PATCH:
        tile = _tile(farm, tile_xy)
        ripe = (isinstance(tile, dict) and tile.get('kind') == 'PLANT'
                and tile.get('crop') == 'MELON')
        if day >= MELON_PATCH_HARVEST_DAY and ripe:
            if int(tile.get('yield_units', 0) or 0) <= 0:
                continue
            return ['HARVEST'] if tuple(pos) == tile_xy else _step_toward(pos, tile_xy)
        if day >= MELON_PATCH_HARVEST_DAY:
            continue
        if tile is None and have_seed > 0 and day >= MELON_PATCH_PLANT_DAY:
            return ['PLANT', 'MELON'] if tuple(pos) == tile_xy else _step_toward(pos, tile_xy)
        # Two consecutive dry days turns the tile to weed, and every watered day
        # from age 6 on is another unit of fruit, so water whatever is dry.
        if ripe and not tile.get('watered_today'):
            return ['WATER'] if tuple(pos) == tile_xy else _step_toward(pos, tile_xy)
    return None


_ROUTE_HANDS_PER_DAY = {}


def _routed_hands(step):
    """How many hands the recording addresses on this step's DAY.

    Not len(_ROUTE[step]['hands']): that list is 0 long at hour 0 and only 7
    long at hour 1 of day 10, when the roster is 14. Reading it per step made
    this layer hand melon jobs to seven hands the route was relying on, at the
    single busiest moment of the game.
    """
    day = step // 24
    if day not in _ROUTE_HANDS_PER_DAY:
        lo, hi = day * 24, min((day + 1) * 24, len(_ROUTE))
        _ROUTE_HANDS_PER_DAY[day] = max(
            (len(_ROUTE[s].get('hands') or []) for s in range(lo, hi)), default=0)
    return _ROUTE_HANDS_PER_DAY[day]


def _melon_patch(action, obs, step):
    if not MELON_PATCH:
        return action
    day = step // 24
    if day > MELON_PATCH_HARVEST_DAY + 2:
        return action

    seat = _player(obs)
    farm = _farm_view(obs, seat)
    hands = list(_value(farm, 'hands', []) or [])
    routed = _routed_hands(step)
    private = _value(obs, 'private', {}) or {}
    action = _copy_plan(action)
    market = [list(o) for o in action.get('market') or []]

    # Keep exactly one hand more than the recording addresses.
    if len(hands) <= routed and len(market) < 10:
        market.append(['HIRE'])

    # The recording sells melon on day 10 and then not again until day 20, by
    # which point the market is dead. The patch ripens on day 11, so without
    # this its fruit would sit in the shed for nine days and fetch $1.
    if day >= MELON_PATCH_HARVEST_DAY:
        private_shed = _value(private, 'shed', {}) or {}
        held = max(0, int(_value(private_shed, 'MELON', 0) or 0))
        if held > 0 and not any(
                len(o) >= 3 and o[0] == 'SELL' and o[1] == 'MELON' for o in market):
            if len(market) < 10:
                market.append(['SELL', 'MELON', held])
    action['market'] = market[:10]

    plan = [list(h or ['PASS']) for h in (action.get('hands') or [])]
    while len(plan) < len(hands):
        plan.append(['PASS'])
    for idx in range(routed, len(hands)):
        # private.inventories is [farmer, *hands], so hand i is at i + 1.
        order = _patch_job(farm, private, idx + 1, hands[idx], day)
        if order:
            plan[idx] = order
    action['hands'] = plan
    return action

#
# The town's eight shops are drawn per episode WITH REPLACEMENT, so how much
# wool and milk the town eats is a per-game fact -- and it is handed to the
# agent in obs.town.unlocked_shops. The recording ignores it and buys the same
# 8 cows and 4 sheep every single game. Over 20 route-vs-route games, WOOL ends
# more than 50 units SHORT at around $240 in 9 of them, while MILK ends 74 units
# LONG at $5 in most. The herd is wrong in both directions at once.
#
# Episode 93781740 is what that costs. The town drew two YARN_STOREs -- single
# product, so two units a tick each -- and wool never fell below $246 all game.
# The opponent ran 8 sheep to our 4 and took $66,063 of wool to our $31,383.
# That one product is a bigger gap than the entire $34,001 match margin.
#
# COW and SHEEP both live on a PASTURE, so this is a rename and nothing more --
# no structure changes, no choreography changes, and PLACE cannot strand an
# animal on the wrong building the way the goose experiment could. Only the
# BUY is a decision; PICKUP and PLACE are corrected to whatever we actually
# hold, so the three can never disagree.
#
# It works, and it is switched OFF, because it wins money and loses games.
# Measured against the stock route over 32 seeds, 128 games:
#
#     PASTURE_TILT None   64/64 wins   our 93,628   theirs 91,222
#     PASTURE_TILT 1.0    54/64 wins   our 94,844   theirs 93,780
#
# In the games where it fires it is worth +$8,500 to +$9,000 and never once
# hurts our own score. It still costs ten wins, because vacating milk hands a
# cow-heavy opponent an uncontested run at it: our score goes up $1,216 and
# theirs goes up $2,558. The reward here is the bank balance but the RANKING is
# win-based, so a change that enriches both sides and the opponent more is a
# losing trade. 0.6, 1.0 and 1.6 all decide identically -- the wool/milk call is
# never close -- so this is the change itself failing, not the threshold.
#
# The "it is right against a sheep-heavy FIELD" defence is now falsified too.
# Replayed against all 138 live episodes with the real opponents' recorded
# actions (bench_losses.py --all):
#
#     PASTURE_TILT None   103W-35L   +$1,074 a game
#     PASTURE_TILT 1.0     96W-42L   +$2,945 a game
#     versus control: 0 gained, 7 lost, net -7 wins
#
# It gains nothing anywhere -- not even in the wool-heavy games it was built
# for, where it makes money without turning it into wins -- and gives back seven.
# So gating it on the opponent's fork cannot save it: there is nothing to gate
# ON. Almost three times the money and seven fewer wins is the exact trade a
# win-rate ladder punishes. Kept only as a worked example of that trap.
# ----------------------------------------------------------------------------
PASTURE_TILT = None

# Day 0 buys 4 sheep and a cow before a single shop has opened, so there is
# nothing to react to; the first shop unlocks on day 3. Everything the route
# buys from here on is a live decision.
PASTURE_DECIDE_STEP = 72

_PASTURE_ANIMALS = ('COW', 'SHEEP')
_PASTURE_PRODUCT = {'COW': 'MILK', 'SHEEP': 'WOOL'}
_PASTURE_COST = {'COW': 400, 'SHEEP': 500}


def _town_rate(obs, item):
    """Units of `item` the town eats per shop tick, from the shops it has opened."""
    town = _value(obs, 'town', {}) or {}
    rate = 0
    for shop in list(_value(town, 'unlocked_shops', []) or []):
        products = _SHOP_DEMAND.get(shop, ())
        if item in products:
            rate += 2 if len(products) == 1 else 1
    return rate


def _preferred_pasture(obs):
    wool = _town_rate(obs, 'WOOL') * _MKT_PARAMS['WOOL'][0]
    milk = _town_rate(obs, 'MILK') * _MKT_PARAMS['MILK'][0]
    return 'SHEEP' if wool > milk * PASTURE_TILT else 'COW'


def _retarget_pasture(action, obs, step):
    if PASTURE_TILT is None:
        return action

    seat = _player(obs)
    farm = _farm_view(obs, seat)
    private = _value(obs, 'private', {}) or {}
    shed = _value(private, 'shed', {}) or {}
    inventories = list(_value(private, 'inventories', []) or [])
    action = _copy_plan(action)

    if step >= PASTURE_DECIDE_STEP:
        want = _preferred_pasture(obs)
        money = float(_value(farm, 'money', 0) or 0)
        for order in action.get('market') or []:
            if (len(order) >= 2 and order[0] == 'BUY_ANIMAL'
                    and order[1] in _PASTURE_ANIMALS and order[1] != want):
                # A sheep costs $100 more than a cow and the route runs its
                # balance down to double digits in the first week. A buy that
                # cannot be afforded is not a worse animal, it is no animal, so
                # only upgrade when the money is already in hand.
                if money >= _PASTURE_COST[want] * (int(order[2]) if len(order) > 2 else 1):
                    order[1] = want

    # PICKUP and PLACE are corrected to what we are actually holding rather than
    # decided again, so a purchase that was retargeted (or refused) still lines
    # up with the animal that reaches the pasture.
    units = [('farmer', action.get('farmer'))]
    units += [(i, h) for i, h in enumerate(action.get('hands') or [])]
    for idx, (_slot, unit) in enumerate(units):
        if not unit or len(unit) < 2 or unit[1] not in _PASTURE_ANIMALS:
            continue
        if unit[0] == 'PICKUP':
            if int(_value(shed, unit[1], 0) or 0) <= 0:
                other = next((a for a in _PASTURE_ANIMALS
                              if int(_value(shed, a, 0) or 0) > 0), None)
                if other:
                    unit[1] = other
        elif unit[0] == 'PLACE':
            inv = inventories[idx] if idx < len(inventories) else {}
            if int(_value(inv, unit[1], 0) or 0) <= 0:
                other = next((a for a in _PASTURE_ANIMALS
                              if int(_value(inv, a, 0) or 0) > 0), None)
                if other:
                    unit[1] = other
    return action


# Applied here, not next to its definition: the edits read MELON_PATCH and
# CARROT_SWAP, which are declared by layers further down the file.
_apply_route_edits()


def agent(obs):
    try:
        _apply_route_edits()
        step = min(max(0, int(_value(obs, 'step', 0) or 0)), len(_ROUTE) - 1)
        action = _repair_weed_block(obs, _copy_plan(_ROUTE[step]), step)
        state = _lead_state(obs, step)
        action = _remove_advanced_qty(action, state, step)
        action = _advance_sale(action, obs, state, step)
        action = _final_drop_cash(obs, action, step)
        action = _retarget_pasture(action, obs, step)
        action = _melon_patch(action, obs, step)
        action = _eager_sell(action, obs, step)
        return _match_hands(action, obs)
    except Exception:
        farm = _farm_view(obs, _player(obs))
        return {'farmer': ['PASS'], 'hands': [['PASS'] for _ in _value(farm, 'hands', []) or []], 'market': []}
