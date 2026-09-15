"""

in block_filtering you are asking each block, what is your contribution to all the peaks except the common one.
then we filter out a certain percentage of the most significant ones.
it gives you the blocks with useful information in them. The problem is we don't know which of the filtered
blocks are more useful for us. some blocks may be including items with hues apart from the common hue yet
of no interest for us. e.g. a river.
to get around this problem, as a next step, we ask every cropped image, what is your contribution to the
 peaks within a certain hue range (of course outside the common-hue-range)?

one cropped image might say: I contain 95% of the pixels whose hues have formed non-zero value in the
 distribution ( of course outside the common hues range).

so we pick a number of blocks from block_filtering, and next, we find the color range (outside the common) to which they contribute.


for every cropped image:
    for every color_range outside the common hue range:
        evaluate the union of the cropped image to the histogram of full frame for the color_range




BASED ON 360 degrees:

RED: 55
320 : 360 | 0 : 15

ORANGE: 25
15: 40

YELLOW: 30
40 : 70

GREEN: 90
70 : 160

BLUE: 105
160: 265

PURPLE: 55
265: 320



in a block:
how much variation of hue/sat/value exist?


"""
import copy

import cv2

import mo_toolkit

from statsmodels.stats.weightstats import DescrStatsW
import numpy as np



hue_color_ranges = [
    [int(0 * 180 / 360), int(40 * 180 / 360)],  # ORANGE 28.33
    [int(40 * 180 / 360), int(70 * 180 / 360)],  # YELLOW
    [int(70 * 180 / 360), int(160 * 180 / 360)],  # GREEN
    [int(160 * 180 / 360), int(265 * 180 / 360)],  # BLUE
    [int(265 * 180 / 360), int(320 * 180 / 360)],  # PURPLE
    [int(320 * 180 / 360), int(360 * 180 / 360)]  # RED
]


def get_st_for_hue_mags(hue_mag_pairs_for_hue_range):
    hues = [x[0] for x in hue_mag_pairs_for_hue_range]
    weights_union_mag = [x[1] for x in hue_mag_pairs_for_hue_range]

    ret = 0.0
    if len(weights_union_mag) == 0:
        return ret

    if max(weights_union_mag) != 0:
        ret = DescrStatsW(hues, weights=weights_union_mag, ddof=0).var

    if not(ret >= 0 ):
        asd =3
    return ret



def cum_mask_all_excluded_hues(img_hsv, hue_bins_to_remove_percentage):

    hue_hist = cv2.calcHist([img_hsv], [0], None, [180], [0, 180])

    hue_bins_sorted = list(np.argsort([-int(x[0]) for x in hue_hist]))


    hue_thresh_idx = 0
    sum_pixels = 0
    while 1:
        sum_pixels += hue_hist[hue_bins_sorted[hue_thresh_idx]][0]
        if sum_pixels >= 320 * 240 * hue_bins_to_remove_percentage / 100:
            break
        hue_thresh_idx += 1

    excluded_hues = hue_bins_sorted[:(hue_thresh_idx + 1)]

    for idx, hue_not_accepted in enumerate(excluded_hues):

        lower_band_mask = np.array([hue_not_accepted, 0, 0])
        upper_band_mask = np.array([hue_not_accepted, 256, 256])

        if idx == 0:
            hue_excluded_mask = cv2.inRange(img_hsv, lower_band_mask, upper_band_mask)
        else:
            hue_excluded_mask = cv2.add(hue_excluded_mask, cv2.inRange(img_hsv, lower_band_mask, upper_band_mask))

    return excluded_hues, hue_excluded_mask






def get_most_significant_block_idxs(blocks_overall_contribution_mags, non_dominated_block_idxs, top_blocks_count):





    """
    dominated_needed = max(0 , top_blocks_count - non_dominated_block_counts)
    total_needed = top_blocks_count
    
    for i:
        if (total_needed > 0):
            if (non dominated):
                pick i
                total_needed -= 1;
                
            else (dominated)
                if (dominated_needed > 0)
                    pick i
                    dominated_needed -= 1
                    
        if total_needed == 0:
            break
            

    """
    ret = []
    most_significant_block_idxs = np.argsort(-np.asarray(blocks_overall_contribution_mags))

    dominated_needed = max(0, top_blocks_count - len(non_dominated_block_idxs))
    total_needed = top_blocks_count

    for idx, block_idx in enumerate(most_significant_block_idxs):

        if (total_needed > 0):
            if (block_idx in non_dominated_block_idxs):
                ret.append(block_idx)
                total_needed -= 1
            else:
                if (dominated_needed > 0):
                    ret.append(block_idx)
                    dominated_needed -= 1
                    total_needed -= 1

        if total_needed == 0:
            break


    return ret


def range_colors(img_rgb,
                 hue_bins_to_remove_percentage,
                 top_blocks_count,
                 ):


    Archive = []

    crop_count = 8

    img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)


    """
    build full frame hue histogram
    """
    hue_hist_full_frame = cv2.calcHist([img_hsv], [0], None, [180], [0, 180])

    remaining_pixels_count_masked = sum([x[0] for x in hue_hist_full_frame])

    hue_hist_full_frame_normalized = hue_hist_full_frame / remaining_pixels_count_masked

    assert np.round(sum([x[0] for x in hue_hist_full_frame_normalized]), 0) == 1

    """
    find the to-be-excluded hues
    """

    excluded_hues, hue_excluded_mask = cum_mask_all_excluded_hues(img_hsv, hue_bins_to_remove_percentage)

    excluded_hues_string=''
    for i in range(180):
        excluded_hues_string = excluded_hues_string + ('1' if i in excluded_hues else '0')

    hue_included_mask = cv2.bitwise_not(hue_excluded_mask)



    """
    
    when we want to generate basepoints, why are we filtering out pixels with excluded hues?
    many pixels with excluded hues need to be encoded and transmitted after all
    I don't see the point
    
    excluded hues only use is to find the most significant blocks
    we only need to exclude the none significant blocks from the image
    in order to produce the basepoints.
    
    
    defend:
    I build my basepoints base on the red, green, and blue values of pixels whose hue is not excluded
    
    objection:
    I don't care if the hue in excluded or not
    we are encoding those pixels anyway if they are within the most significant blocks
    so to make efficient use of or bpus, we need to biuld our basepoints based on every pixel that is being encoded
    those are every pixels within the significant blocks. regardless of their hues
    by excluding hues we are left with very few pixels which can never provide the right base
    for generating an efficient base point. that is why we need to go through recursion to fill our base points.
    
    
    """

    """
    1) ------------------------------------------------------------------------- HUE COMPARISON
    deduct the undesired pixels from hue_hist_full_frame
    """

    hue_hist_full_frame_deducted = copy.deepcopy(hue_hist_full_frame)

    for excluded_hue in excluded_hues:
        hue_hist_full_frame_deducted[excluded_hue] = 0

    """
    and normalize the histogram to unity
    """

    remaining_pixels_count_desired = sum([x[0] for x in hue_hist_full_frame_deducted])
    hue_hist_full_frame_deducted_normalized = hue_hist_full_frame_deducted / remaining_pixels_count_desired
    assert np.round(sum([x[0] for x in hue_hist_full_frame_deducted_normalized]), 0) == 1



    height_cropped = int(240 / crop_count)
    width_cropped = int(320 / crop_count)


    hue_desired_unions_mag = np.zeros(shape=[crop_count, crop_count, len(hue_color_ranges)])
    hue_desired_unions_sd = np.zeros(shape=[crop_count, crop_count, len(hue_color_ranges)])


    blocks_width_height_idxs = []
    blocks_overall_contribution_mags = []
    blocks_overall_contribution_sds = []


    """
    we use the block's full normalizes histogram to compare with the full frame deducted and normalized hostogram.
    but then we deduct the excluded hues from the blocks histogram in order to find the g-mapper base points based on
    the given sum_bpu.
    
    """
    block_counter = 0

    for crop_idx_height in range(crop_count):

        for crop_idx_width in range(crop_count):

            cropped_img = img_hsv[
                          crop_idx_height * height_cropped: (crop_idx_height + 1) * height_cropped,
                          crop_idx_width * width_cropped: (crop_idx_width + 1) * width_cropped
                          ]

            """
            use the normalized hue histogram of the block to compare with
                the normalized deducted hue histogram of the full frame 
            """
            hue_hist_cropped_img = cv2.calcHist([cropped_img], [0], None, [180], [0, 180])


            remaining_pixels_count = sum([int(x[0]) for x in hue_hist_cropped_img])

            assert remaining_pixels_count == width_cropped * height_cropped

            hue_hist_cropped_img_normalized = hue_hist_cropped_img / remaining_pixels_count

            union_mags = copy.deepcopy(hue_hist_cropped_img_normalized)
            for i in range(union_mags.shape[0]):
                union_mags[i][0] = 0.




            for hue_color_range_idx, hue_color_range in enumerate(hue_color_ranges):

                hue_mag_pairs_for_hue_range = []

                cropped_img_hue_desired_union_magnitude = 0

                for hue in range(hue_color_range[0], hue_color_range[1]):

                    if hue not in excluded_hues:

                        union_mag = min(hue_hist_cropped_img_normalized[hue][0], hue_hist_full_frame_deducted_normalized[hue][0])

                        union_mags[hue] = union_mag

                        hue_mag_pairs_for_hue_range.append([hue, union_mag])

                        cropped_img_hue_desired_union_magnitude += pow(union_mag, 2)


                hue_desired_unions_mag[crop_idx_height][crop_idx_width][hue_color_range_idx
                ] = cropped_img_hue_desired_union_magnitude

                """
                calculate the sd for the union values within the hue range
                """

                range_st = get_st_for_hue_mags(hue_mag_pairs_for_hue_range)
                assert range_st >= 0
                hue_desired_unions_sd[crop_idx_height][crop_idx_width][hue_color_range_idx
                ] = range_st


            blocks_width_height_idxs.append((crop_idx_height, crop_idx_width))

            blocks_overall_contribution_mag = sum(hue_desired_unions_mag[crop_idx_height][crop_idx_width])
            blocks_overall_contribution_sd = sum(hue_desired_unions_sd[crop_idx_height][crop_idx_width])


            blocks_overall_contribution_mags.append(blocks_overall_contribution_mag)
            blocks_overall_contribution_sds.append(blocks_overall_contribution_sd)

            snew = mo_toolkit.solution(1, 2)
            snew.dv = [block_counter]
            snew.f = [-blocks_overall_contribution_mag, -blocks_overall_contribution_sd]
            if block_counter == 0:
                Archive.append(snew)
            else:
                Archive, _ = mo_toolkit.Update_Archive(Archive, snew)


            block_counter += 1


    """
    now we pick the blocks with most significant contributions.
    among the chosen ones, the ones with highest rank, are codded with their high sum_bpu (gmapper_basepoints_high)
    the ones with lowest rank, are codded with low sum_bpu (gmapper_basepoints_low)
    
    """

    non_dominated_block_idxs=[x.dv[0] for x in Archive]

    most_significant_block_idxs = get_most_significant_block_idxs(blocks_overall_contribution_mags, non_dominated_block_idxs, top_blocks_count)


    most_significant_block_idxs_string=''
    for i in range(crop_count*crop_count):
        most_significant_block_idxs_string = most_significant_block_idxs_string + ('1' if i in most_significant_block_idxs else '0')


    most_significant_block_width_height_idxs = []

    most_significant_block_idxs.sort()

    for idx, most_significant_block_idx in enumerate(most_significant_block_idxs):
        most_significant_block_width_height_idxs.append(blocks_width_height_idxs[most_significant_block_idx])



    """
    building the final mask based on most_significant_blocks
    """
    final_mask = np.ones(img_hsv.shape[:2], dtype="uint8")

    block_counter = 0
    for crop_idx_height in range(crop_count):

        for crop_idx_width in range(crop_count):

            if block_counter not in most_significant_block_idxs:

                cv2.rectangle(
                    final_mask,
                    (crop_idx_width * width_cropped, crop_idx_height * height_cropped),
                    ((crop_idx_width + 1) * width_cropped, (crop_idx_height + 1) * height_cropped),
                    (0, 0, 0),
                    -1)

            block_counter += 1


    return final_mask
