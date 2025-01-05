// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// the skull data
const skull = `
M 499.99946 50
C 334.8433 50 200.97514 164.43042 200.97514 321.9675
C 200.97514 420.80423 253.66685 468.60947 333.7191 519.7946
L 333.7191 594.22944
C 346.09998 605.76466 360.18906 615.93 375.62135 624.5974
L 375.62135 575.25586
L 397.40467 594.8824
L 397.40467 635.3901
C 425.18863 647.3862 456.4036 654.6069 489.4874 655.836
L 489.4874 594.8824
L 511.2561 594.8824
L 511.2561 655.77196
C 541.7703 654.4405 570.57626 647.9623 596.6082 637.3617
L 596.6082 594.8824
L 618.39154 575.25586
L 618.39154 627.2476
C 635.7364 618.05524 651.5337 606.9681 665.1702 594.24224
L 665.1702 520.49876
C 745.8211 469.39043 799.0384 421.27793 799.0384 321.9675
C 799.0092 164.41762 665.1556 50 499.99946 50
Z
M 381.4906 460.2493
C 327.70387 460.2493 284.10802 422.0205 284.10802 374.8554
C 284.10802 327.6903 327.70387 327.2294 381.4906 327.2294
C 435.2773 327.2294 478.87314 327.6903 478.87314 374.8554
C 478.87314 422.0205 435.2773 460.2493 381.4906 460.2493
Z
M 482.66916 525.5174
C 471.4855 535.24746 456.1116 537.59035 448.31516 530.6769
C 440.5187 523.80185 443.26353 510.3462 454.4618 500.6034
C 465.66006 490.86054 481.03395 488.55606 488.8304 495.4183
C 496.62684 502.28054 493.8528 515.76177 482.66916 525.5174
Z
M 551.69836 530.6769
C 543.9019 537.59035 528.5134 535.23465 517.32976 525.5174
C 506.1461 515.76177 503.4013 502.29334 511.1977 495.4183
C 518.97957 488.55606 534.36806 490.86054 545.5517 500.6034
C 556.7208 510.3462 559.4802 523.80185 551.69836 530.6769
Z
M 618.50834 460.2493
C 564.7216 460.2493 521.1258 422.0205 521.1258 374.8554
C 521.1258 327.6903 564.7216 327.2294 618.50834 327.2294
C 672.29505 327.2294 715.8909 327.6903 715.8909 374.8554
C 715.8909 422.0205 672.29505 460.2493 618.50834 460.2493
Z
M 925.9131 650.8813
C 882.2297 673.32444 836.8526 650.49725 836.8526 650.49725
L 586.66556 778.8954
L 646.5551 809.5962
C 646.5551 809.5962 691.9176 786.7947 735.6156 809.225
C 758.8005 821.0931 766.597 847.2233 753.0189 867.554
C 744.4633 880.3567 729.4836 887.7695 713.7447 888.5632
C 720.7089 900.969 720.6797 916.0506 712.0949 928.8789
C 698.546 949.2096 668.7472 956.0334 645.5769 944.1397
C 601.87884 921.7222 602.36065 875.863 602.36065 875.863
L 499.99946 823.3591
L 397.66747 875.8758
C 397.66747 875.8758 398.12007 921.735 354.43662 944.1525
C 331.2663 956.0462 301.48212 949.2224 287.88944 928.8917
C 279.3484 916.0634 279.3192 900.969 286.25423 888.576
C 270.52994 887.7823 255.50646 880.3695 246.98 867.5668
C 233.40193 847.2361 241.18377 821.1059 264.3833 809.2378
C 308.06676 786.8075 353.4438 809.609 353.4438 809.609
L 413.31876 778.9082
L 163.14633 650.49725
C 163.14633 650.49725 117.78387 673.32444 74.085815 650.8813
C 50.88628 639.01324 43.104437 612.88295 56.667915 592.5523
C 65.208964 579.7496 80.24705 572.32404 95.95674 571.5303
C 89.0363 559.1245 89.0509 544.0429 97.60655 531.2146
C 111.18463 510.89675 140.9688 504.0729 164.15373 515.9666
C 207.83718 538.3713 207.36998 584.24334 207.36998 584.24334
L 499.99946 734.4189
L 792.6435 584.25614
C 792.6435 584.25614 792.1617 538.3841 835.8598 515.9794
C 859.0447 504.0857 888.8289 510.90955 902.3778 531.2274
C 910.9626 544.0557 910.9772 559.1501 904.013 571.5431
C 919.7665 572.33684 934.7608 579.7624 943.3018 592.5651
C 956.9091 612.88295 949.1272 639.01324 925.9131 650.8813
Z`


// render the shape
export const Skull = ({ style }) => {
    // mix my paint
    const ico = { ...styles.icon, ...style?.icon }

    // paint me
    return (
        <path d={skull} style={ico} />
    )
}


// end of file
