
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from package import optimize_loading, calculate_utilization
from package import visualize_container


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Container Loading Optimizer",
    page_icon="📦",
    layout="wide"
)


# ==========================================
# 2. APPLICATION TITLE
# ==========================================

st.title("📦 Container Loading Optimizer")

st.write(
    "Optimize package placement inside a container "
    "using an intelligent 2D packing algorithm."
)

st.divider()


# ==========================================
# 3. CONTAINER DIMENSIONS
# ==========================================

st.header("1. Container Details")

col1, col2 = st.columns(2)

with col1:

    container_width = st.number_input(
        "Container Width",
        min_value=1,
        max_value=100,
        value=10,
        step=1
    )

with col2:

    container_height = st.number_input(
        "Container Height",
        min_value=1,
        max_value=100,
        value=8,
        step=1
    )


# ==========================================
# 4. PACKAGE DETAILS
# ==========================================

st.header("2. Package Details")

st.write(
    "Enter package IDs and their dimensions. "
    "Use the + button to add more packages."
)

default_packages = pd.DataFrame({
    "Package ID": ["P1", "P2", "P3", "P4", "P5", "P6", "P7"],
    "Width": [4, 3, 2, 5, 2, 3, 2],
    "Height": [3, 3, 4, 2, 2, 2, 3]
})

package_data = st.data_editor(
    default_packages,
    num_rows="dynamic",
    use_container_width=True,
    key="package_editor"
)


# ==========================================
# 5. OPTIMIZATION BUTTON
# ==========================================

st.divider()

if st.button("🚀 Optimize Container Loading", type="primary"):

    try:

        packages = {}

        # Validate package information
        for _, row in package_data.iterrows():

            if pd.isna(row["Package ID"]) or not str(row["Package ID"]).strip():
                continue

            package_id = str(row["Package ID"]).strip()

            if pd.isna(row["Width"]) or pd.isna(row["Height"]):
                raise ValueError(
                    f"Missing dimensions for {package_id}"
                )

            width = int(row["Width"])
            height = int(row["Height"])

            if width <= 0 or height <= 0:
                raise ValueError(
                    f"Dimensions must be positive for {package_id}"
                )

            if package_id in packages:
                raise ValueError(
                    f"Duplicate package ID: {package_id}"
                )

            packages[package_id] = (width, height)

        if not packages:
            raise ValueError("Please enter at least one package.")

        # Run optimization
        with st.spinner("Finding the best arrangement..."):

            placements, unplaced = optimize_loading(
                packages,
                int(container_width),
                int(container_height)
            )

        # Calculate performance
        used_area, total_area, utilization = calculate_utilization(
            placements,
            int(container_width),
            int(container_height)
        )

        # ==================================
        # 6. DISPLAY RESULTS
        # ==================================

        st.success("Optimization completed successfully!")

        st.header("3. Optimization Results")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Packages Placed",
            f"{len(placements)}/{len(packages)}"
        )

        col2.metric(
            "Space Utilization",
            f"{utilization:.2f}%"
        )

        col3.metric(
            "Used Area",
            used_area
        )

        col4.metric(
            "Unused Area",
            total_area - used_area
        )

        # ==================================
        # 7. VISUALIZATION
        # ==================================

        st.subheader("Optimized Container Layout")

        fig = visualize_container(
            placements,
            int(container_width),
            int(container_height)
        )

        st.pyplot(fig)
        plt.close(fig)

        # ==================================
        # 8. PACKAGE PLACEMENT DETAILS
        # ==================================

        st.subheader("Package Placement Details")

        if placements:

            result_df = pd.DataFrame(placements)

            st.dataframe(
                result_df,
                use_container_width=True,
                hide_index=True
            )

            csv_data = result_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Download Placement Results",
                data=csv_data,
                file_name="container_placement_results.csv",
                mime="text/csv"
            )

        else:
            st.info("No packages were placed, so there are no placement results to download.")

        if unplaced:

            st.warning(
                "The following packages could not be placed: "
                + ", ".join(unplaced)
            )

        else:

            st.success("All packages were successfully placed!")

        # ==================================
        # 9. UTILIZATION SUMMARY
        # ==================================

        st.subheader("Space Utilization Analysis")

        st.progress(
            min(1.0, utilization / 100)
        )

        st.write(
            f"**Container capacity utilized: "
            f"{utilization:.2f}%**"
        )

        st.write(
            f"Remaining space: {total_area - used_area} "
            f"square units"
        )

    except (ValueError, TypeError, KeyError, OverflowError) as error:

        st.error(f"Input Error: {error}")
