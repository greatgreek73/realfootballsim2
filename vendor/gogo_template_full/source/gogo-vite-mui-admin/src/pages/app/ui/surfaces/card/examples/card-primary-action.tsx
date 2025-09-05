import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import CardMedia from "@mui/material/CardMedia";
import Typography from "@mui/material/Typography";

export default function CardPrimaryAction() {
  return (
    <Card className="max-w-80">
      <CardActionArea>
        <CardMedia component="img" alt="product" className="h-48 rounded-md" image="/images/products/product-1.jpg" />
        <CardContent>
          <Typography gutterBottom variant="h5" component="h5">
            Card Action
          </Typography>
          <Typography variant="body1" className="text-text-secondary">
            Lizards are a widespread group of squamate reptiles, with over 6,000 species, ranging across all continents
            except Antarctica
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
