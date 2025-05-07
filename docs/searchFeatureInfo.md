# Search Feature info

## How To Use
- Look for Search link on the left sidebar
- Select what you want to search from dropdown and search

## How it works
It starts here in the `GROUP_PROJECT\unihub_project\templates\pages\search_page.html` file. You can look at the javascript I've commented it. 

But basically, based on the drop down box it will determine the API endpoint. So far I only have users so it will be redirected to the `UserSearchAPI` endpoint. 


I then also add the users input into the query part of the url, so I can use it at whatever API endpoint im redirected to.
```
if (searchType === 'users') {
        apiUrl = `/api/search/users/?query=${query}`;
    }

// fetch sends the HTTP request
fetch(apiUrl)
```

<br>
API endpoint for searching users:

```
class UserSearchAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]  

    def get(self, request):
        query = request.GET.get('query', None)
        if query:
            user_profile_list = User.objects.filter(    # filters based on username, provided from search query
                Q(username__icontains=query)
            ).exclude(id=request.user.id) # dont't include the current user

            users_data = [
                {
                    "username": user.username, 
                    "user_type": user.user_type,
                    "university": user.university
                } 
                for user in user_profile_list
            ]
            return Response(users_data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No search query provided."}, status=status.HTTP_400_BAD_REQUEST)

```
I use a `Q` object here to query what I need from the db. It was in this video: https://www.youtube.com/watch?v=yDJZk761Iik 
but essentially it lets you perform logical operations on queries, so I could if I wanted to say username OR university.

Then this will return a response back to `GROUP_PROJECT\unihub_project\templates\pages\search_page.html`, where I construct a html div of the search results to display them.
```
 // Displaying search results for the different search types
            // Only done users for now, ill do communities and tags later
            if (searchType === 'users') {
                resultsDiv.innerHTML = '<h4>Users</h4>';
                const userList = document.createElement('div');
                userList.className = 'list-group';
                
                // loop through users from the response
                data.forEach(user => {
                    const userItem = document.createElement('a');
                    userItem.className = 'list-group-item list-group-item-action';
                    userItem.innerHTML = `
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">${user.username}</h5>
                            <small>${user.user_type}</small>
                        </div>
                        <p class="mb-1">${user.university || 'University not specified'}</p>
                    `;
                    userList.appendChild(userItem);
                });
                
                resultsDiv.appendChild(userList);
```







