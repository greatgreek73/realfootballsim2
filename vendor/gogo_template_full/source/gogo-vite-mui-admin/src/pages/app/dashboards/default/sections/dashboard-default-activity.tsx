import { Link } from "react-router-dom";

import Timeline from "@mui/lab/Timeline";
import TimelineConnector from "@mui/lab/TimelineConnector";
import TimelineContent from "@mui/lab/TimelineContent";
import TimelineDot from "@mui/lab/TimelineDot";
import TimelineItem from "@mui/lab/TimelineItem";
import TimelineSeparator from "@mui/lab/TimelineSeparator";
import { Card, CardContent, Typography } from "@mui/material";

export default function DashboardDefaultActivity() {
  return (
    <Card className="h-full">
      <Typography variant="h5" component="h5" className="card-title px-4 pt-4">
        Activity
      </Typography>
      <CardContent className="pt-0! pr-0!">
        <Timeline className="h-[500px] items-start overflow-auto">
          <TimelineItem>
            <TimelineSeparator>
              <TimelineDot color="info" variant="outlined" />
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="subtitle2" className="text-text-primary">
                Permission Updated
              </Typography>
              <Typography variant="body2" className="text-text-secondary line-clamp-1">
                Olivia updated user permissions for{" "}
                <Link to="/#" className="link-text-secondary">
                  Elijah
                </Link>
              </Typography>
              <Typography variant="body2" className="text-text-disabled">
                4 hours ago
              </Typography>
            </TimelineContent>
          </TimelineItem>

          <TimelineItem>
            <TimelineSeparator>
              <TimelineDot color="success" variant="outlined" />
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="subtitle2" className="text-text-primary">
                User Login
              </Typography>
              <Typography variant="body2" className="text-text-secondary line-clamp-1">
                <Link to="/#" className="link-text-secondary">
                  Olivia
                </Link>{" "}
                logged into the admin dashboard.
              </Typography>
              <Typography variant="body2" className="text-text-disabled">
                4 hours ago
              </Typography>
            </TimelineContent>
          </TimelineItem>

          <TimelineItem>
            <TimelineSeparator>
              <TimelineDot color="info" variant="outlined" />
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="subtitle2" className="text-text-primary">
                Product Update
              </Typography>
              <Typography variant="body2" className="text-text-secondary line-clamp-1">
                Charlotte edited product details for{" "}
                <Link to="/#" className="link-text-secondary">
                  Buck Rogers
                </Link>
              </Typography>
              <Typography variant="body2" className="text-text-disabled">
                6 hours ago
              </Typography>
            </TimelineContent>
          </TimelineItem>

          <TimelineItem>
            <TimelineSeparator>
              <TimelineDot color="warning" variant="outlined" />
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="subtitle2" className="text-text-primary">
                Refund Process
              </Typography>
              <Typography variant="body2" className="text-text-secondary line-clamp-1">
                James processed refund request for order{" "}
                <Link to="/#" className="link-text-secondary">
                  #10234
                </Link>
              </Typography>
              <Typography variant="body2" className="text-text-disabled">
                2 days ago
              </Typography>
            </TimelineContent>
          </TimelineItem>

          <TimelineItem>
            <TimelineSeparator>
              <TimelineDot color="error" variant="outlined" />
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="subtitle2" className="text-text-primary">
                Comment Delete
              </Typography>
              <Typography variant="body2" className="text-text-secondary line-clamp-1">
                James deleted flagged{" "}
                <Link to="/#" className="link-text-secondary">
                  comment
                </Link>{" "}
                on product Wooden Bunny
              </Typography>
              <Typography variant="body2" className="text-text-disabled">
                2 days ago
              </Typography>
            </TimelineContent>
          </TimelineItem>

          <TimelineItem>
            <TimelineSeparator>
              <TimelineDot color="info" variant="outlined" />
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="subtitle2" className="text-text-primary">
                Page Publish
              </Typography>
              <Typography variant="body2" className="text-text-secondary line-clamp-1">
                James published a new blog post:{" "}
                <Link to="/#" className="link-text-secondary">
                  Simple Toys for Creativity
                </Link>
              </Typography>
              <Typography variant="body2" className="text-text-disabled">
                2 days ago
              </Typography>
            </TimelineContent>
          </TimelineItem>

          <TimelineItem>
            <TimelineSeparator>
              <TimelineDot color="info" variant="outlined" />
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="subtitle2" className="text-text-primary">
                Image Update
              </Typography>
              <Typography variant="body2" className="text-text-secondary line-clamp-1">
                James updated{" "}
                <Link to="/#" className="link-text-secondary">
                  website banner
                </Link>{" "}
                image for the homepage.
              </Typography>
              <Typography variant="body2" className="text-text-disabled">
                3 days ago
              </Typography>
            </TimelineContent>
          </TimelineItem>

          <TimelineItem>
            <TimelineSeparator>
              <TimelineDot color="success" variant="outlined" />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="subtitle2" className="text-text-primary">
                User Login
              </Typography>
              <Typography variant="body2" className="text-text-secondary line-clamp-1">
                <Link to="/#" className="link-text-secondary">
                  James
                </Link>{" "}
                logged into the admin dashboard.
              </Typography>
              <Typography variant="body2" className="text-text-disabled">
                3 days ago
              </Typography>
            </TimelineContent>
          </TimelineItem>
        </Timeline>
      </CardContent>
    </Card>
  );
}
