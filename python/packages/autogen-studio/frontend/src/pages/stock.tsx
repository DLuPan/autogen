import * as React from "react";
import Layout from "../components/layout";
import { graphql } from "gatsby";
import StockManager from "../components/views/stock/manager";

// markup
const StockPage = ({ data }: any) => {
    return (
        <Layout meta={data.site.siteMetadata} title="Home" link={"/stock"}>
            <main style={{ height: "100%" }} className=" h-full ">
                <StockManager />
            </main>
        </Layout>
    );
};

export const query = graphql`
  query HomePageQuery {
    site {
      siteMetadata {
        description
        title
      }
    }
  }
`;

export default StockPage;
