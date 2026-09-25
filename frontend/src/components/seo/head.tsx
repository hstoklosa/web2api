import { Helmet } from "react-helmet-async";

type HeadProps = {
  title?: string;
  description?: string;
};

export const Head = ({ title, description }: HeadProps) => {
  return (
    <Helmet
      title={title}
      titleTemplate="%s | web2api"
      defaultTitle="web2api"
    >
      {description && (
        <meta
          name="description"
          content={description}
        />
      )}
    </Helmet>
  );
};
