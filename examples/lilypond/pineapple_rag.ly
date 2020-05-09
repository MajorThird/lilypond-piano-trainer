
\new GrandStaff   <<
\new Staff {
\key bes \major
\time 2/4
  g'16\mf f'8 ees'16 d'( cis' d' c') bes( c' d' f') ~ f'4 g'16 g'8 fis'16 g'( a' bes'8) c'' f' ~ f' f' \break \repeat volta 2 {
    < bes' d'' g'' >16\mf f''8 ees''16 d''( cis'' d'' c'') bes'( c'' d'' f'') ~ f'' bes'' < f'' d''' >8 < bes' d'' g'' >16 f''8 ees''16 d''( cis'' d'' ees'') < bes' d'' f'' >8\< < bes' f'' >16( d'') < bes' f'' >( d'' < bes' f'' >8\!) bes'16(\f < ees'' bes'' >8) bes'16( < ees'' bes'' >8) bes'16( < ees'' bes'' >) ~ < ees'' bes'' > d'''( bes'' d'') << { f''( e'' f'' g'') } \\ { bes'4 } >> a''16( < c'' f'' >8) a''16( < bes' e'' g'' >8) < bes' e'' a'' >16 < a' f'' > ~ < a' f'' >8 a'16( bes' c'' d'' ees'' f'') \break < bes' d'' g'' >\mf f''8 ees''16 d''( cis'' d'' c'') bes'( c'' d'' f'') ~ f'' bes'' < f'' d''' >8 < bes' d'' g'' >16 f''8 ees''16 d''( cis'' d'' ees'') < bes' d'' f'' >8 < bes' f'' >16 d'' < bes' f'' >( d'' < bes' f'' >8) \pageBreak bes'16(\f < ees'' bes'' >8) bes'16( < ees'' bes'' >8) bes'16( < ees'' bes'' >) ~ < ees'' bes'' > d'''( bes'' f'') d''( f'' g'' bes'')
  } \alternative { { << {
         bes'4 c''16 d''8 bes'16 ~ bes'8[ bes'16^( c''] \revert Stem.direction
         d''[ ees'') < a' ees'' f'' >8]
       } \\ {
         \revert NoteColumn.horizontal-shift
         e'( ees') < ees' a' >8.[ d'16] ~ \override Stem.direction = #1
         d'4 s
       } >> } { << {
         bes'4 c''16 d''8 bes'16 ~ bes'8[ f'16( e'] f' fis' g' gis')
       } \\ {
         e'8( ees') < ees' a' >8.[ d'16] ~ \revert Stem.direction
         d'4 s
       } >> } }
}




\new Staff {
\key bes \major
\time 2/4
\clef bass
g16 f8 ees16 d( cis d c) bes,( c d f) ~ f4 g16 g8 fis16 g( a bes8) c' f ~ f f \repeat volta 2 {
  bes, < f bes d' > f, < f bes d' > bes, < f bes d' > f, < f bes d' > bes, < f bes d' > f, < f bes d' > bes,[( d f aes)] << { g < g bes ees' > ges < ges bes ees' > } \\ { < g, g >4 < ges, ges > } >> < f, f >8 < f bes d' > < d, d >( < des, des >) < c, c > < a c' f' > < c, c > < bes c' e' > < f, f >[ c( a, f,)] bes, < f bes d' > f, < f bes d' > bes, < f bes d' > f, < f bes d' > bes, < f bes d' > f, < f bes d' > bes,[( d f aes)] << { g < g bes ees' > ges < ges bes ees' > } \\ { < g, g >4 < ges, ges > } >> < f, f >8 < f bes d' > < f, f > < f bes d' >
} \alternative { {
  < g, g >8( < ges, ges >) < f, f >4 < bes, bes >8 r r < f, f >
} {
  < g, g >8( < ges, ges >) < f, f >4 < bes, bes >8 r r < b, b >
} }
}

 >>
